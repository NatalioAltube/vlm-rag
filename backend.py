# backend.py
# -----------------------------------------
# Gestión de documentos PDF, embeddings y retrieval por página
# -----------------------------------------

import os
import fitz  # PyMuPDF
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document as LangDocument
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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

# 2. Embedding por página usando modelo local
def embed_documents_by_page(pages: List[LangDocument]) -> FAISS:
    # Usar modelo local de sentence-transformers
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}  # Usar CPU por defecto
    )
    return FAISS.from_documents(pages, embeddings)

# 3. Retrieval de página más relevante
def retrieve_relevant_page(faiss_db: FAISS, query: str) -> LangDocument:
    results = faiss_db.similarity_search(query, k=1)
    return results[0] if results else None

