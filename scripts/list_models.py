import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG")
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Beschikbare modellen die embeddings ondersteunen:")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"- {m.name}")
