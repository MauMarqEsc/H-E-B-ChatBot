import os
from pypdf import PdfReader
import streamlit as st
from config.settings import POLITICS_FOLDER
from prompts.words_to_avoid import AVOID_WORDS

@st.cache_data
def load_policies():
    #---- Lee y extrae textos de los PDF's de la carpeta politicas  ----#
    pages = []
    folder = POLITICS_FOLDER if os.path.exists(POLITICS_FOLDER) else "politicas"

    if not os.path.exists(folder):
        return pages

    for file in os.listdir(folder):
        if file.lower().endswith(".pdf"):
            pdf_route = os.path.join(folder, file)
            try:
                reader = PdfReader(pdf_route)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            "document": file,
                            "page": i +1,
                            "content": text.strip()
                        })
            except Exception as e:
                print(f"Error leyendo archivo {file}: {e}")
    return pages

def search_in_policies(question):
    #---- En base a la pregunta se buscan fragmentos dentro del PDF ----#
    pages = load_policies()

    stop_words = AVOID_WORDS

    words = [
        w.lower().strip("?,.!:;\"'") 
        for w in question.split() 
        if w.lower().strip("?,.!:;\"'") not in stop_words and len(w) > 2
    ]
    
    if not words:
        words = [w.lower().strip("?,.!:;\"'") for w in question.split() if len(w) > 2]
    
    scored = []
    for p in pages:
        p_text_lower = p["content"].lower()
        score = sum(p_text_lower.count(w) for w in words)
        if score > 0:
            scored.append((score, p))
    if not scored:
        return "No se encontraron referencias directas sobre el tema en las políticas internas."

    scored.sort(key=lambda x: x[0], reverse=True)

    answer = "**Extractos de Políticas y Normativas Relevantes:**\n\n"
    for score, res in scored[:2]:
        answer += f"### Documento: `{res['document']}` (Página {res['page']})\n"
        answer += f"{res['content'][:1200]}\n\n"
    return answer