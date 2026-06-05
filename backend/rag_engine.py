import httpx
import json
import logging
from pinecone import Pinecone
from openai import AsyncOpenAI
from .config import config

logger = logging.getLogger(__name__)

# Initialize Pinecone
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.PINECONE_INDEX_NAME)

# Initialize OpenAI-compatible NVIDIA NIM client
client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=config.NVIDIA_API_KEY
)

# Global reusable HTTP client to leverage keep-alive connections
httpx_client = httpx.AsyncClient(timeout=30.0)

RELEVANCE_THRESHOLD = 0.20  # Lowered from 0.35 to catch conversational Vapi queries

async def get_embedding(text: str) -> list:
    """Get embedding vector for the search query using NVIDIA NIM"""
    url = "https://integrate.api.nvidia.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {config.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "input": [text],
        "model": config.NVIDIA_EMBED_MODEL,
        "input_type": "query",
        "encoding_format": "float"
    }
    
    try:
        response = await httpx_client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["embedding"]
        else:
            logger.error(f"Error getting embedding: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"HTTP error getting embedding: {e}", exc_info=True)
        return []

async def search_knowledge(query: str, top_k: int = 5) -> str:
    """Search Pinecone for relevant knowledge chunks based on query"""
    logger.info(f"[RAG] Searching for: '{query}' (top_k={top_k})")
    
    embedding = await get_embedding(query)
    
    if not embedding:
        return "Error generating search embedding."
        
    try:
        # Search Pinecone
        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results with relevance filtering
        context_chunks = []
        for match in results["matches"]:
            score = match.get("score", 0)
            source = match["metadata"].get("source", "unknown")
            text = match["metadata"].get("text", "")
            section = match["metadata"].get("section", "")
            
            logger.info(f"[RAG] Chunk: score={score:.3f}, source={source}, section={section}, preview={text[:80]}...")
            
            # Filter out low-relevance chunks
            if score < RELEVANCE_THRESHOLD:
                logger.info(f"[RAG] Skipping chunk (score {score:.3f} < threshold {RELEVANCE_THRESHOLD})")
                continue
            
            section_label = f", Section: {section}" if section else ""
            context_chunks.append(f"[Source: {source}{section_label}, Relevance: {score:.2f}]\n{text}\n")
        
        if not context_chunks:
            logger.warning(f"[RAG] No chunks passed relevance threshold for query: '{query}'")
            return "No highly relevant information found in the knowledge base for this specific query."
            
        result = "\n".join(context_chunks)
        logger.info(f"[RAG] Returning {len(context_chunks)} relevant chunks ({len(result)} chars)")
        return result
        
    except Exception as e:
        logger.error(f"Error searching Pinecone: {e}", exc_info=True)
        return "Error accessing knowledge base."

async def generate_chat_response(messages: list, stream: bool = False, max_tokens: int = 500):
    """Generate response using NVIDIA NIM Llama 3.1 70B"""
    try:
        response = await client.chat.completions.create(
            model=config.NVIDIA_LLM_MODEL,
            messages=messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=16384,
            stream=stream
        )
        return response
    except Exception as e:
        logger.error(f"Error calling LLM: {e}", exc_info=True)
        raise e

async def generate_voice_response(messages: list) -> str:
    """Generate a non-streaming response optimized for voice (shorter, faster)"""
    try:
        response = await client.chat.completions.create(
            model=config.NVIDIA_LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,  # Shorter for voice
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM for voice: {e}", exc_info=True)
        raise e
