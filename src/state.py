import os
import json
from datetime import datetime, timedelta

class StateTracker:
    """Maneja la persistencia del estado del pipeline (checkpoints e intervalos de tiempo)."""
    
    def __init__(self, filepath: str = "checkpoint.json"):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
                # Convertimos la lista del JSON a un 'set' en memoria para búsquedas O(1)
                content["processed_ids"] = set(content.get("processed_ids", []))
                return content
        
        # Estado inicial por defecto si el archivo no existe
        return {
            "last_sync_date": "01-Jan-2025", # Fecha base de inicio del proyecto
            "processed_ids": set()
        }

    def save(self):
        """Persiste el estado actual en el archivo JSON."""
        to_save = {
            "last_sync_date": self.data["last_sync_date"],
            "processed_ids": list(self.data["processed_ids"]) # Convertimos a lista para JSON
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=4)

    def get_since_date_for_imap(self) -> str:
        """
        Retorna la fecha formateada para IMAP (ej: '19-Jul-2025').
        Resta 1 día a la última sincronización por seguridad ante desfases de zonas horarias.
        """
        last_date_str = self.data["last_sync_date"]
        last_date = datetime.strptime(last_date_str, "%d-%b-%Y")
        safe_date = last_date - timedelta(days=1)
        return safe_date.strftime("%d-%b-%Y")

    def is_already_processed(self, msg_id: str) -> bool:
        return msg_id in self.data["processed_ids"]

    def mark_as_processed(self, msg_id: str):
        self.data["processed_ids"].add(msg_id)

    def update_sync_date(self):
        """Establece el día de hoy como la última fecha de sincronización exitosa."""
        self.data["last_sync_date"] = datetime.now().strftime("%d-%b-%Y")