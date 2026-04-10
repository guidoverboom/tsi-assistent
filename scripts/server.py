from flask import Flask, request, jsonify
from flask_cors import CORS
import query_agent
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

from datetime import datetime

def log_activity(question, result):
    log_path = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG/user_activity.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources = ", ".join(result['sources'])
    
    log_entry = f"""
## [{timestamp}] Nieuwe Interactie
**Vraag:** 
{question}

**Antwoord:** 
{result['answer']}

**Bronnen:** {sources}

---
"""
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "Geen vraag opgegeven"}), 400
    
    try:
        result = query_agent.query_rag(question)
        log_activity(question, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"Server draait op http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
