import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG")
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Beschikbare modellen:")
try:
    for m in client.models.list():
        print(f"- {m.name}")
except Exception as e:
    print(f"Fout bij ophalen modellen: {e}")
