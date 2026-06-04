import httpx
import json
from pinecone import Pinecone
from openai import AsyncOpenAI
from .config import config

# Initialize Pinecone
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.PINECONE_INDEX_NAME)

# Initialize OpenAI-compatible NVIDIA NIM client
client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=config.NVIDIA_API_KEY
)

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
    
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["embedding"]
        else:
            print(f"Error getting embedding: {response.text}")
            return []

async def search_knowledge(query: str, top_k: int = 5) -> str:
    """Search Pinecone for relevant knowledge chunks based on query"""
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
        
        # Format results
        context_chunks = []
        for match in results["matches"]:
            source = match["metadata"].get("source", "unknown")
            text = match["metadata"].get("text", "")
            context_chunks.append(f"[Source: {source}]\n{text}\n")
            
        return "\n".join(context_chunks)
    except Exception as e:
        print(f"Error searching Pinecone: {e}")
        return "Error accessing knowledge base."

async def generate_chat_response(messages: list, stream: bool = False):
    """Generate response using NVIDIA NIM Llama 3.1 70B"""
    try:
        response = await client.chat.completions.create(
            model=config.NVIDIA_LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            stream=stream
        )
        return response
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise e
