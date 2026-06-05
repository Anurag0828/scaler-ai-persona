import os
import json
import re
import requests
import PyPDF2
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "scaler-persona")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "Anurag0828")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Files
RESUME_PDF_PATH = "../Anurag_Sajwan_Resume_Final-2.pdf"
DATA_DIR = "../data"

# Resume section headers to detect for metadata tagging
RESUME_SECTIONS = [
    "education", "experience", "work experience", "professional experience",
    "skills", "technical skills", "projects", "certifications",
    "achievements", "summary", "objective", "contact"
]

def detect_resume_section(text: str) -> str:
    """Detect which resume section a chunk belongs to based on content keywords."""
    text_lower = text.lower()
    
    # Check for explicit section headers
    for section in RESUME_SECTIONS:
        if section in text_lower[:100]:  # Check near the top of the chunk
            return section.replace(" ", "_")
    
    # Heuristic detection based on content
    if any(kw in text_lower for kw in ["university", "degree", "b.tech", "m.tech", "cgpa", "gpa", "bachelor", "master"]):
        return "education"
    elif any(kw in text_lower for kw in ["developer", "engineer", "intern", "company", "role", "responsibilities", "worked at"]):
        return "experience"
    elif any(kw in text_lower for kw in ["python", "javascript", "react", "fastapi", "langchain", "docker", "kubernetes"]):
        return "skills"
    elif any(kw in text_lower for kw in ["project", "built", "developed", "implemented", "created"]):
        return "projects"
    
    return "general"

def extract_resume_text(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text = "\n".join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def fetch_github_repos(username, token=None):
    print(f"Fetching GitHub repos for {username}...")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    response = requests.get(repos_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching repos: {response.status_code} - {response.text}")
        return []
    
    repos = response.json()
    repo_data = []
    
    for repo in repos:
        # Skip forks
        if repo["fork"]:
            continue
            
        print(f"Fetching details for {repo['name']}...")
        
        # Get languages
        langs_url = repo["languages_url"]
        langs_response = requests.get(langs_url, headers=headers)
        languages = list(langs_response.json().keys()) if langs_response.status_code == 200 else []
        
        # Get README
        readme_url = f"https://api.github.com/repos/{username}/{repo['name']}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        readme_text = ""
        if readme_response.status_code == 200:
            import base64
            readme_data = readme_response.json()
            if "content" in readme_data:
                try:
                    readme_text = base64.b64decode(readme_data["content"]).decode('utf-8')
                except:
                    pass
        
        repo_info = {
            "name": repo["name"],
            "description": repo["description"] or "",
            "languages": languages,
            "url": repo["html_url"],
            "stars": repo.get("stargazers_count", 0),
            "readme": readme_text
        }
        repo_data.append(repo_info)
        
    return repo_data

def get_embeddings(texts, input_type="passage"):
    print(f"Getting embeddings for {len(texts)} chunks...")
    url = "https://integrate.api.nvidia.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "input": texts,
        "model": NVIDIA_EMBED_MODEL,
        "input_type": input_type,
        "encoding_format": "float"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error getting embeddings: {response.status_code} - {response.text}")
        raise Exception(f"Embedding API error: {response.text}")
        
    data = response.json()
    embeddings = [item["embedding"] for item in data["data"]]
    return embeddings

def setup_pinecone():
    print(f"Setting up Pinecone index: {PINECONE_INDEX_NAME}...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"Creating new index {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1024, # e5-v5 dimension is 1024
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        import time
        while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            print("Waiting for index to be ready...")
            time.sleep(2)
    else:
        # Clear existing vectors for clean re-ingestion
        print("Index exists. Clearing existing vectors for clean re-ingestion...")
        idx = pc.Index(PINECONE_INDEX_NAME)
        try:
            idx.delete(delete_all=True, namespace="")
            print("Cleared existing vectors.")
        except Exception as e:
            print(f"Note: Could not clear vectors (may already be empty): {e}")
            
    return pc.Index(PINECONE_INDEX_NAME)

def create_talking_points_chunks():
    """Create curated talking points about why to hire Anurag."""
    talking_points = [
        {
            "id": "talking_points_why_hire",
            "text": """Why Hire Anurag Sajwan:
- Full-stack AI engineer with hands-on experience building autonomous agents, RAG pipelines, and production ML systems
- Proven ability to ship end-to-end: from data ingestion to deployment (FastAPI, Docker, Render, Vercel)
- Strong understanding of modern AI stack: LangChain, LangGraph, vector databases (Pinecone, ChromaDB), NVIDIA NIM
- Built this very AI persona system as a demonstration of autonomous agent capabilities
- Combines software engineering discipline with AI/ML expertise
- Quick learner who can go from concept to production independently""",
            "metadata": {"source": "talking_points", "section": "why_hire"}
        },
        {
            "id": "talking_points_tech_philosophy",
            "text": """Anurag's Technical Philosophy and Approach:
- Believes in building production-grade systems, not just prototypes
- Focuses on RAG over fine-tuning for knowledge-grounded applications because it provides better control, auditability, and cost-efficiency
- Prefers open-source models (NVIDIA NIM, Llama) for flexibility and cost control
- Values comprehensive documentation and testing as part of the engineering process
- Approaches problems methodically: understand requirements, design architecture, implement iteratively, test thoroughly""",
            "metadata": {"source": "talking_points", "section": "philosophy"}
        }
    ]
    return talking_points

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Parse Resume
    resume_text = extract_resume_text(os.path.join(os.path.dirname(__file__), RESUME_PDF_PATH))
    with open(os.path.join(DATA_DIR, "resume.txt"), "w", encoding="utf-8") as f:
        f.write(resume_text)
    print(f"Resume extracted: {len(resume_text)} characters")
        
    # 2. Fetch GitHub Repos
    github_repos = fetch_github_repos(GITHUB_USERNAME, GITHUB_TOKEN)
    with open(os.path.join(DATA_DIR, "github_repos.json"), "w", encoding="utf-8") as f:
        json.dump(github_repos, f, indent=2)
    print(f"GitHub repos fetched: {len(github_repos)} repos")
        
    # 3. Chunk Data — IMPROVED: Larger chunks with more overlap for better context
    print("\nChunking data...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # Increased from 500 → 800 for more context per chunk
        chunk_overlap=200,    # Increased from 100 → 200 for better continuity
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    
    # Chunk resume with section detection
    resume_chunks = text_splitter.split_text(resume_text)
    print(f"Resume split into {len(resume_chunks)} chunks")
    for i, chunk in enumerate(resume_chunks):
        section = detect_resume_section(chunk)
        chunks.append({
            "id": f"resume_chunk_{i}",
            "text": chunk,
            "metadata": {
                "source": "resume", 
                "section": section,
                "chunk_index": i
            }
        })
        print(f"  Chunk {i}: section={section}, length={len(chunk)}, preview: {chunk[:80]}...")
        
    # Chunk GitHub repos — NO CAP on chunks per repo
    for repo in github_repos:
        repo_context = f"GitHub Repository: {repo['name']}\nDescription: {repo['description']}\nLanguages: {', '.join(repo['languages'])}\nURL: {repo['url']}\nStars: {repo.get('stars', 0)}\n\nREADME:\n"
        
        # Split README — removed the 6-chunk cap
        readme_chunks = text_splitter.split_text(repo["readme"])
        if not readme_chunks:
            # If no readme, just add the repo metadata
            chunks.append({
                "id": f"github_repo_{repo['name']}_meta",
                "text": repo_context,
                "metadata": {"source": "github", "repo": repo["name"], "section": "repo_metadata"}
            })
            continue
        
        print(f"Repo '{repo['name']}': {len(readme_chunks)} README chunks")
        
        for i, chunk in enumerate(readme_chunks):
            # NO CAP — all README content is indexed
            combined_text = repo_context + chunk
            chunks.append({
                "id": f"github_repo_{repo['name']}_chunk_{i}",
                "text": combined_text,
                "metadata": {"source": "github", "repo": repo["name"], "section": "readme"}
            })
    
    # Add talking points
    talking_points = create_talking_points_chunks()
    for tp in talking_points:
        chunks.append(tp)
    print(f"Added {len(talking_points)} talking points chunks")
            
    print(f"\n{'='*50}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"  Resume chunks: {sum(1 for c in chunks if c['metadata'].get('source') == 'resume')}")
    print(f"  GitHub chunks: {sum(1 for c in chunks if c['metadata'].get('source') == 'github')}")
    print(f"  Talking points: {sum(1 for c in chunks if c['metadata'].get('source') == 'talking_points')}")
    print(f"{'='*50}\n")
    
    # 4. Initialize Pinecone (clears existing vectors)
    index = setup_pinecone()
    
    # 5. Embed and Upsert in batches
    batch_size = 40  # Slightly reduced to avoid NVIDIA API limits
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [item["text"] for item in batch]
        
        embeddings = get_embeddings(texts, input_type="passage")
        
        vectors_to_upsert = []
        for j, item in enumerate(batch):
            metadata = item["metadata"].copy()
            metadata["text"] = item["text"] # Store text so we can retrieve it
            
            vectors_to_upsert.append((
                item["id"],
                embeddings[j],
                metadata
            ))
            
        print(f"Upserting batch {i//batch_size + 1} ({len(vectors_to_upsert)} vectors)...")
        index.upsert(vectors=vectors_to_upsert, namespace="")
        
    print("\n[OK] Ingestion complete!")
    print(f"Total vectors in Pinecone: {len(chunks)}")

if __name__ == "__main__":
    main()
