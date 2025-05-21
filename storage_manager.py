import os
import json
import time
from datetime import datetime
from pathlib import Path
import shutil

class StorageManager:
    def __init__(self):
        self.base_storage_path = Path("storage")
        self.pdfs_path = self.base_storage_path / "pdfs"
        self.metrics_path = self.base_storage_path / "metrics"
        self._initialize_storage()

    def _initialize_storage(self):
        """Inicializa la estructura de directorios necesaria"""
        self.pdfs_path.mkdir(parents=True, exist_ok=True)
        self.metrics_path.mkdir(parents=True, exist_ok=True)

    def save_pdf(self, pdf_bytes: bytes, filename: str, user_id: str) -> dict:
        """Guarda un PDF y registra métricas"""
        start_time = time.time()
        
        # Crear directorio del usuario si no existe
        user_pdf_path = self.pdfs_path / user_id
        user_pdf_path.mkdir(exist_ok=True)
        
        # Guardar PDF
        file_path = user_pdf_path / filename
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Registrar métricas
        metrics = {
            "filename": filename,
            "user_id": user_id,
            "size_bytes": len(pdf_bytes),
            "upload_time": datetime.now().isoformat(),
            "upload_duration": time.time() - start_time
        }
        
        self._save_metrics(metrics)
        return metrics

    def delete_pdf(self, filename: str, user_id: str) -> bool:
        """Elimina un PDF específico"""
        file_path = self.pdfs_path / user_id / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def delete_all_user_pdfs(self, user_id: str) -> bool:
        """Elimina todos los PDFs de un usuario"""
        user_pdf_path = self.pdfs_path / user_id
        if user_pdf_path.exists():
            shutil.rmtree(user_pdf_path)
            return True
        return False

    def get_user_pdfs(self, user_id: str) -> list:
        """Obtiene lista de PDFs de un usuario"""
        user_pdf_path = self.pdfs_path / user_id
        if not user_pdf_path.exists():
            return []
        
        return [f.name for f in user_pdf_path.glob("*.pdf")]

    def _save_metrics(self, metrics: dict):
        """Guarda métricas en un archivo JSON"""
        metrics_file = self.metrics_path / "upload_metrics.json"
        
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                existing_metrics = json.load(f)
        else:
            existing_metrics = []
        
        existing_metrics.append(metrics)
        
        with open(metrics_file, "w") as f:
            json.dump(existing_metrics, f, indent=2)

    def get_metrics(self) -> dict:
        """Obtiene métricas de rendimiento"""
        metrics_file = self.metrics_path / "upload_metrics.json"
        if not metrics_file.exists():
            return {
                "total_uploads": 0,
                "total_size": 0,
                "avg_upload_time": 0
            }
        
        with open(metrics_file, "r") as f:
            metrics = json.load(f)
        
        total_size = sum(m["size_bytes"] for m in metrics)
        avg_upload_time = sum(m["upload_duration"] for m in metrics) / len(metrics) if metrics else 0
        
        return {
            "total_uploads": len(metrics),
            "total_size": total_size,
            "avg_upload_time": avg_upload_time
        } 