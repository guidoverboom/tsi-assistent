import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from tqdm import tqdm

# Configuratie
BASE_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG")
VERWERKT_DIR = BASE_DIR / "verwerkt"
INDEX_DIR = BASE_DIR / "index"
ENV_FILE = BASE_DIR / ".env"

# Laad API Key
load_dotenv(ENV_FILE)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Fout: Geen GOOGLE_API_KEY gevonden in .env")
    exit(1)

client = genai.Client(api_key=api_key)

def chunk_text(text, filename, chunk_size=1000, overlap=200):
    """Eenvoudige chunking met overlap."""
    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) > chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            # Bewaar wat overlap (ongeveer)
            overlap_lines = current_chunk[-3:] if len(current_chunk) > 3 else []
            current_chunk = overlap_lines + [line]
            current_length = sum(len(l) for l in current_chunk)
        else:
            current_chunk.append(line)
            current_length += len(line)
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return [{"text": c, "source": filename} for c in chunks]

import time

def create_embeddings():
    if not INDEX_DIR.exists():
        INDEX_DIR.mkdir(parents=True)

    output_path = INDEX_DIR / "knowledge_base.json"
    
    # Laad bestaande kennisbank als die er is
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
        processed_files = set([item['source'] for item in knowledge_base])
        print(f"Bestaande kennisbank geladen met {len(processed_files)} bestanden.")
    else:
        knowledge_base = []
        processed_files = set()

    markdown_files = list(VERWERKT_DIR.glob("*.md"))
    
    # Sorteer alfabetisch voor voorspelbaar gedrag
    markdown_files.sort()

    print(f"Start indexering van {len(markdown_files)} bestanden met gemini-embedding-001...")

    for md_path in markdown_files:
        if md_path.name in processed_files:
            print(f"Overslaan: {md_path.name} (al in index)")
            continue
            
        print(f"Verwerken: {md_path.name}")
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = chunk_text(content, md_path.name)
        
        for item in tqdm(chunks, desc=f"Embeddings voor {md_path.name}"):
            retries = 3
            while retries > 0:
                try:
                    result = client.models.embed_content(
                        model='gemini-embedding-001',
                        contents=item["text"]
                    )
                    item["embedding"] = result.embeddings[0].values
                    knowledge_base.append(item)
                    # Kleine pauze om rate limits te respecteren (free tier)
                    time.sleep(1.2) 
                    break 
                except Exception as e:
                    if "429" in str(e):
                        print(f"\nRate limit bereikt. Wachten... (Nog {retries} pogingen)")
                        time.sleep(10)
                        retries -= 1
                    else:
                        print(f"Fout bij embedding voor chunk in {md_path.name}: {e}")
                        break

        # Opslaan van de voortgang na elk bestand
        output_path = INDEX_DIR / "knowledge_base.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
            
        print(f"Kennisbank bijgewerkt met {md_path.name}. Totaal chunks: {len(knowledge_base)}")

    print(f"Volledige indexeringsproces voltooid.")

if __name__ == "__main__":
    create_embeddings()
