# vision_ollama.py
# ----------------------------------------
# Render y envío de imagen de página relevante a LLaVA (Ollama)
# ----------------------------------------

import os
import base64
import tempfile
import fitz  # PyMuPDF
import requests
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuración de Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava:13b"  # Modelo VLM de Ollama

class VisionMetrics:
    def __init__(self):
        self.metrics_path = Path("storage/metrics")
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.metrics_path / "vision_metrics.json"

    def save_metrics(self, metrics: dict):
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                existing_metrics = json.load(f)
        else:
            existing_metrics = []
        
        existing_metrics.append(metrics)
        
        with open(self.metrics_file, "w") as f:
            json.dump(existing_metrics, f, indent=2)

# Renderizar página como imagen PNG y devolver ruta (NO se elimina automáticamente)
def render_page_as_image(pdf_bytes: bytes, page_number: int) -> str:
    temp_img_path = tempfile.mktemp(suffix=".png")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number - 1)
    pix = page.get_pixmap(dpi=200)
    pix.save(temp_img_path)
    return temp_img_path

# Enviar imagen a LLaVA (Ollama) como base64-encoded PNG
def ask_question_to_vlm(pdf_bytes: bytes, question: str, page_number: int = None) -> str:
    """
    Mantiene la misma interfaz que vision_api.py para compatibilidad
    """
    try:
        start_time = time.time()
        metrics = VisionMetrics()
        
        # Si no se especifica página, usar la primera
        if not page_number:
            page_number = 1
        
        image_path = render_page_as_image(pdf_bytes, page_number)
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode()

        prompt = f"""Analiza el documento proporcionado y responde la siguiente pregunta: {question}

Instrucciones generales:
1. Analiza detalladamente el contenido del documento, incluyendo texto, tablas, gráficos y datos numéricos.
2. Identifica y menciona cualquier dato relevante, valores, fechas, resultados o hallazgos importantes.
3. Si hay tablas o gráficos, incluye los datos relevantes en tu respuesta.
4. Si la información solicitada no está presente en la página {page_number}, indícalo claramente.

Instrucciones específicas por tipo de documento:
- Si el documento contiene información médica: Analiza el contenido como material de estudio académico, proporcionando una interpretación detallada de los hallazgos, valores y resultados presentes. Trata la información como un caso de estudio para fines educativos.
- Si el documento es técnico/legal/mecánico: Proporciona un análisis detallado basado en la información presente, manteniendo un enfoque técnico y profesional.

IMPORTANTE: Proporciona una respuesta completa basada en la información disponible en el documento. No sugieras consultas externas ni restricciones de interpretación.

Pregunta específica: {question}
Página a analizar: {page_number}"""

        # Preparar el payload para Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "images": [encoded_image],
            "stream": False
        }

        # Realizar la petición a Ollama
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # Extraer la respuesta
        result = response.json()
        answer = result.get("response", "No se pudo obtener una respuesta del modelo")

        # Calcular métricas
        processing_time = time.time() - start_time
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "page_processed": page_number,
            "processing_time": processing_time,
            "response": answer
        }
        
        metrics.save_metrics(metrics_data)
        
        return answer

    except Exception as e:
        error_msg = f"[Error al consultar el modelo]: {e}"
        if 'start_time' in locals():
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "page_processed": page_number,
                "processing_time": time.time() - start_time,
                "error": error_msg
            }
            metrics.save_metrics(metrics_data)
        return error_msg 