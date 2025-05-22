import hashlib
from datetime import datetime
from database import DatabaseManager

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.active_user = None

    def register(self, username: str, password: str, email: str = None) -> bool:
        if self.db.get_user(username):
            return False  # usuario ya existe
        password_hash = hash_password(password)
        fecha_registro = datetime.now().isoformat()
        self.db.insert_user(username, password_hash, email, fecha_registro)
        return True

    def login(self, username: str, password: str):
        user = self.db.get_user(username)
        if not user:
            return None
        if user[2] == hash_password(password):  # password_hash está en posición 2
            self.active_user = user
            return user  # retorna toda la fila, por ej. (id, username, password_hash, ...)
        return None
    
    def logout(self):
        # Limpiar variables de sesión locales
        self.active_user = None
        # Aquí puedes agregar limpieza de archivos temporales si se usan
        print("Sesión cerrada correctamente.")
    
