import sys
from pathlib import Path

# Voeg scripts map toe aan path
sys.path.append("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG/scripts")
import query_agent

questions = [
    "Welke kwantitatieve doelen (KPI's) voor 2025 of 2030 worden genoemd in de nota's van MTB, DCW, Amfors of Stark?",
    "Worden er specifieke financiële bedragen genoemd (budgetten, unit-costs, besparingen) die in een dashboard passen?",
    "Welke specifieke sectoren (bijv. zorg, techniek) worden als speerpunten genoemd voor werkontwikkeling?",
    "Wat zijn de belangrijkste strategische thema's (bijv. mens centraal, locatieontwikkeling) die in alle nota's terugkomen?"
]

print("# ANALYSE VOOR STARTFOTO INTEGRATIE\n")

for q in questions:
    print(f"## VRAAG: {q}")
    result = query_agent.query_rag(q)
    print(f"ANTWOORD:\n{result['answer']}\n")
    print(f"BRONNEN: {', '.join(result['sources'])}\n")
    print("-" * 50)
