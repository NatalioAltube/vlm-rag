# backend.py
# -----------------------------------------
# Gestión de documentos PDF, embeddings y retrieval por página
# -----------------------------------------

import os
import fitz  # PyMuPDF
from typing import List
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document as LangDocument
from dotenv import load_dotenv

# Cargar API Key desde .env
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 1. Extraer texto por página para granularidad visual
def extract_text_by_page(file_bytes: bytes, file_name: str) -> List[LangDocument]:
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    documents = []
    for i, page in enumerate(pdf):
        text = page.get_text()
        metadata = {
            "page": i + 1,
            "source": file_name
        }
        documents.append(LangDocument(page_content=text, metadata=metadata))
    return documents

# 2. Embedding por página
def embed_documents_by_page(pages: List[LangDocument]) -> FAISS:
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(pages, embeddings)

# 3. Retrieval de página más relevante
def retrieve_relevant_page(faiss_db: FAISS, query: str) -> LangDocument:
    results = faiss_db.similarity_search(query, k=1)
    return results[0] if results else None

