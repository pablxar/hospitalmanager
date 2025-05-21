from datetime import datetime
from database import DatabaseManager

class AnalysisManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def save_analysis(self, usuario_id: int, nombre: str, archivo_bytes: bytes):
        fecha = datetime.now().isoformat()
        self.db.insert_analysis(usuario_id, nombre, fecha, archivo_bytes)

    def get_user_analyses(self, usuario_id: int):
        return self.db.fetch_analyses_by_user(usuario_id)

    def get_analysis_file(self, analysis_id: int):
        result = self.db.fetch_analysis_file(analysis_id)
        if result:
            return result[0]
        return None
