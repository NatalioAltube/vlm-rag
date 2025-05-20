# vision_api.py
# ----------------------------------------
# Render y envío de imagen de página relevante a GPT-4 Vision
# ----------------------------------------

import openai
import os
import base64
import tempfile
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Renderizar página como imagen PNG y devolver ruta (NO se elimina automáticamente)
def render_page_as_image(pdf_bytes: bytes, page_number: int) -> str:
    temp_img_path = tempfile.mktemp(suffix=".png")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number - 1)
    pix = page.get_pixmap(dpi=200)
    pix.save(temp_img_path)
    return temp_img_path

# Enviar imagen a GPT-4 Vision como base64-encoded PNG
def ask_question_to_vlm(pdf_bytes: bytes, question: str, page_number: int = None) -> str:
    try:
        image_path = render_page_as_image(pdf_bytes, page_number)
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode()

        prompt = f"Respondé esta pregunta basándote en el documento adjunto: {question}"
        if page_number:
            prompt += f". Concentrate en la página {page_number}."

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": """Eres un asistente experto en análisis de documentos. Tu tarea es:
                1. Analizar cuidadosamente el contenido del documento proporcionado
                2. Proporcionar respuestas precisas y detalladas basadas en la información disponible
                3. Si la información no está presente en el documento, indicarlo claramente
                4. Mantener un tono profesional y objetivo
                5. Estructurar las respuestas de manera clara y organizada"""},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                    ]
                }
            ],
            max_tokens=1200
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"[Error al consultar el modelo]: {e}"

