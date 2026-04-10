import fitz  # PyMuPDF
import os
from pathlib import Path

# Configuratie
SOURCE_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG/bronnen")
OUTPUT_DIR = Path("/Users/guido/Library/CloudStorage/OneDrive-Cedris/Product Development/RAG/verwerkt")

def process_pdfs():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    pdf_files = list(SOURCE_DIR.glob("*.pdf")) + list(SOURCE_DIR.glob("*.PDF"))
    # Verwijder dubbelen indien aanwezig
    pdf_files = list(set(pdf_files))
    print(f"Gevonden bestanden: {[f.name for f in pdf_files]}")

    for pdf_path in pdf_files:
        print(f"Bezig met verwerken van: {pdf_path.name}")
        try:
            doc = fitz.open(pdf_path)
            markdown_content = f"# {pdf_path.stem}\n\n"
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                markdown_content += f"## Pagina {page_num + 1}\n\n{text}\n\n"
            
            output_filename = pdf_path.stem.replace(" ", "_") + ".md"
            output_path = OUTPUT_DIR / output_filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            print(f"Succesvol opgeslagen: {output_filename}")
            doc.close()
        except Exception as e:
            print(f"Fout bij verwerken van {pdf_path.name}: {e}")

if __name__ == "__main__":
    process_pdfs()
