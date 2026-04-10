import os
import json
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Configuratie
BASE_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG")
INDEX_PATH = BASE_DIR / "index" / "knowledge_base.json"
ENV_FILE = BASE_DIR / ".env"

# Laad API Key
load_dotenv(ENV_FILE)
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def query_rag(question, top_k=12):
    # 1. Laad kennisbank
    if not INDEX_PATH.exists():
        return "Fout: Kennisbank niet gevonden. Run eerst index_documents.py."
    
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # 2. Embed de vraag
    q_embed_result = client.models.embed_content(
        model='gemini-embedding-001',
        contents=question
    )
    q_embedding = q_embed_result.embeddings[0].values

    # 3. Zoek relevante chunks
    similarities = []
    for item in kb:
        sim = cosine_similarity(q_embedding, item["embedding"])
        similarities.append((sim, item))
    
    # Sorteer op overeenkomst
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Diverse selectie: Pak de top resultaten, maar probeer bronnen te mixen
    selected_chunks = []
    seen_sources = {}
    
    for sim, item in similarities:
        source = item["source"]
        # Maximaal 4 chunks per bron bij een top_k van 12
        if seen_sources.get(source, 0) < 4:
            selected_chunks.append(item)
            seen_sources[source] = seen_sources.get(source, 0) + 1
        
        if len(selected_chunks) >= top_k:
            break
            
    relevant_chunks = selected_chunks

    # 4. Stel context samen
    context = "\n\n".join([f"Bron: {c['source']}\n{c['text']}" for c in relevant_chunks])

    # 5. Laad basisprompt en genereer antwoord
    prompt_path = BASE_DIR / "scripts" / "basisprompt.txt"
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()
    else:
        base_prompt = "Hulp bij vraag: {question}\nContext: {context}"

    prompt = base_prompt.format(context=context, question=question)

    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt
    )
    
    return {
        "answer": response.text,
        "sources": list(set([c['source'] for c in relevant_chunks]))
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = query_rag(query)
        print("\n=== ADVIES ===\n")
        print(result["answer"])
        print("\n=== GEBRUIKTE BRONNEN ===")
        for s in result["sources"]:
            print(f"- {s}")
    else:
        print("Gebruik: python3 query_agent.py 'Je vraag hier'")
