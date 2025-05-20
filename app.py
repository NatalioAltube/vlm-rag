# app.py
# ----------------------------------------
# Interfaz Streamlit para cargar PDFs, hacer preguntas y mostrar respuestas del VLM
# ----------------------------------------
import streamlit as st
from backend import extract_text_by_page, embed_documents_by_page, retrieve_relevant_page
from vision_api import ask_question_to_vlm, render_page_as_image
import tempfile
from PIL import Image
from login import check_auth
import base64
import os

check_auth()

# Inicializar autenticación
def get_logo_base64(logo_path):
    with open(logo_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Configuración de la página
st.set_page_config(page_title="EbalQuiz", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
# Extraer color azul del logo (aprox: #3A7BD5)
PRIMARY_COLOR = "#3A7BD5"
BG_COLOR = "#F5F8FB"
CHAT_USER = "#DCF8C6"  # Verde claro tipo WhatsApp
CHAT_BOT = PRIMARY_COLOR

# Inyectar CSS personalizado
st.markdown(f"""
    <style>
    .ebal-header {{
        display: flex;
        align-items: center;
        background: {BG_COLOR};
        padding: 0.5rem 1.2rem 0.3rem 1.2rem;
        border-radius: 0 0 12px 12px;
        margin-bottom: 0.7rem;
    }}
    .ebal-logo {{
        height: 32px;
        margin-right: 10px;
    }}
    .ebal-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {PRIMARY_COLOR};
        letter-spacing: 0.5px;
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.4em 1.1em;
    }}
    .chat-bubble-user {{
        background: {CHAT_USER};
        color: #222;
        border-radius: 14px 14px 0 14px;
        padding: 0.5em 1em;
        margin: 0.3em 0 0.3em auto;
        max-width: 60%;
        font-size: 1rem;
        text-align: right;
    }}
    .chat-bubble-bot {{
        background: {CHAT_BOT};
        color: white;
        border-radius: 14px 14px 14px 0;
        padding: 0.5em 1em;
        margin: 0.3em auto 0.3em 0;
        max-width: 60%;
        font-size: 1rem;
        text-align: left;
    }}
    .stTextInput>div>div>input {{
        font-size: 1rem;
        padding: 0.5em 0.8em;
        border-radius: 8px;
    }}
    .stFileUploader {{
        font-size: 0.95rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CABECERA CON LOGO Y NOMBRE ---
logo_path = os.path.join(os.getcwd(), "1673777935481.jpg")
logo_b64 = get_logo_base64(logo_path)
st.markdown(f"""
<div class="ebal-header">
    <img src="data:image/png;base64,{logo_b64}" class="ebal-logo" />
    <span class="ebal-title">EbalQuiz</span>
</div>
""", unsafe_allow_html=True)

# Botón de logout
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# Subida de archivos y selección de pregunta
uploaded_files = st.file_uploader("Subí uno o más documentos PDF", type="pdf", accept_multiple_files=True)

# Inicializar historial de chat en session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Cada elemento: {"role": "user"/"bot", "text": str, "img_path": str or None}

# Mostrar historial de chat (burbujas)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["text"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "bot":
        st.markdown(f'<div class="chat-bubble-bot">{msg["text"]}</div>', unsafe_allow_html=True)
        if msg.get("img_path"):
            st.image(msg["img_path"], caption="Página relevante", use_column_width=True)

# Input de pregunta y botón de enviar al final
with st.form(key="chat_form", clear_on_submit=True):
    question = st.text_input("¿Qué querés preguntar?", key="chat_input")
    submit = st.form_submit_button("Enviar pregunta")

if submit and uploaded_files and question:
    with st.spinner("Procesando documentos y buscando respuesta..."):
        all_pages = []
        for file in uploaded_files:
            file_bytes = file.read()
            pages = extract_text_by_page(file_bytes, file.name)
            for page in pages:
                page.metadata["_file_bytes"] = file_bytes
            all_pages.extend(pages)
        faiss_db = embed_documents_by_page(all_pages)
        most_relevant_page = retrieve_relevant_page(faiss_db, question)
        page_number = most_relevant_page.metadata.get("page")
        source_name = most_relevant_page.metadata.get("source")
        file_bytes = most_relevant_page.metadata.get("_file_bytes")
        img_path = render_page_as_image(file_bytes, page_number)
        answer = ask_question_to_vlm(file_bytes, question, page_number=page_number)
        # Guardar pregunta y respuesta en el historial
        st.session_state.chat_history.append({"role": "user", "text": question})
        st.session_state.chat_history.append({"role": "bot", "text": answer, "img_path": img_path})
        st.rerun()

# Botón para limpiar historial de chat
if st.button("🗑️ Limpiar chat"):
    st.session_state.chat_history = []
    st.rerun()