import os
import json
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

def extract_resume_text(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text = "".join([page.extract_text() for page in reader.pages])
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
        # Skip forks if we only want original work, but let's include all for now or filter
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
            
    return pc.Index(PINECONE_INDEX_NAME)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Parse Resume
    resume_text = extract_resume_text(os.path.join(os.path.dirname(__file__), RESUME_PDF_PATH))
    with open(os.path.join(DATA_DIR, "resume.txt"), "w", encoding="utf-8") as f:
        f.write(resume_text)
        
    # 2. Fetch GitHub Repos
    github_repos = fetch_github_repos(GITHUB_USERNAME, GITHUB_TOKEN)
    with open(os.path.join(DATA_DIR, "github_repos.json"), "w", encoding="utf-8") as f:
        json.dump(github_repos, f, indent=2)
        
    # 3. Chunk Data
    print("Chunking data...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = []
    
    # Chunk resume
    resume_chunks = text_splitter.split_text(resume_text)
    for i, chunk in enumerate(resume_chunks):
        chunks.append({
            "id": f"resume_chunk_{i}",
            "text": chunk,
            "metadata": {"source": "resume", "type": "experience_education"}
        })
        
    # Chunk GitHub repos
    for repo in github_repos:
        repo_context = f"Repo: {repo['name']}\nDescription: {repo['description']}\nLanguages: {', '.join(repo['languages'])}\nURL: {repo['url']}\n\nREADME Excerpt:\n"
        
        # Split README
        readme_chunks = text_splitter.split_text(repo["readme"])
        if not readme_chunks:
            # If no readme, just add the repo metadata
            chunks.append({
                "id": f"github_repo_{repo['name']}_meta",
                "text": repo_context,
                "metadata": {"source": "github", "repo": repo["name"]}
            })
            continue
            
        for i, chunk in enumerate(readme_chunks):
            # Limit number of chunks per repo to avoid blowing up DB with huge readmes
            if i > 5: break 
            
            combined_text = repo_context + chunk
            chunks.append({
                "id": f"github_repo_{repo['name']}_chunk_{i}",
                "text": combined_text,
                "metadata": {"source": "github", "repo": repo["name"]}
            })
            
    print(f"Total chunks created: {len(chunks)}")
    
    # 4. Initialize Pinecone
    index = setup_pinecone()
    
    # 5. Embed and Upsert in batches
    batch_size = 50
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
            
        print(f"Upserting batch {i//batch_size + 1}...")
        index.upsert(vectors=vectors_to_upsert, namespace="")
        
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
