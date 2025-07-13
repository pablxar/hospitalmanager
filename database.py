import os
import sys
import sqlite3

def resource_path(relative_path):
    """Obtiene la ruta absoluta, funciona tanto en desarrollo como en .exe empaquetado"""
    try:
        # PyInstaller crea esta variable temporal donde extrae los archivos
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_connection():
    db_path = resource_path("app_data.db")  # Ajusta el nombre si tu base se llama distinto
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

class DatabaseManager:
    def __init__(self):
        self.connection = get_connection()
        # Verifica si las tablas ya existen antes de intentar crearlas
        if not self.tables_exist():
            self.create_tables()

    def tables_exist(self):
        """Verifica si las tablas ya existen en la base de datos."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('usuarios', 'analyses', 'reports');"
        with self.connection:
            result = self.connection.execute(query).fetchall()
        return len(result) == 3  # Devuelve True si todas las tablas existen

    def create_tables(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    fecha_registro TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    file_content BLOB NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    report BLOB NOT NULL
                )
            """)

    # Usuarios
    def insert_user(self, username, password_hash, email, fecha_registro):
        with self.connection:
            self.connection.execute(
                "INSERT INTO usuarios (username, password_hash, email, fecha_registro) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, fecha_registro)
            )

    def get_user(self, username):
        with self.connection:
            return self.connection.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()

    # Analyses
    def insert_analysis(self, usuario_id, name, date, file_content):
        with self.connection:
            self.connection.execute(
                "INSERT INTO analyses (usuario_id, name, date, file_content) VALUES (?, ?, ?, ?)",
                (usuario_id, name, date, file_content)
            )

    def fetch_analyses_by_user(self, usuario_id):
        with self.connection:
            return self.connection.execute(
                "SELECT id, name, date FROM analyses WHERE usuario_id = ? ORDER BY date DESC",
                (usuario_id,)
            ).fetchall()

    def fetch_analysis_file(self, analysis_id):
        with self.connection:
            return self.connection.execute(
                "SELECT file_content FROM analyses WHERE id = ?",
                (analysis_id,)
            ).fetchone()

    def delete_analysis_by_id(self, analysis_id):
        with self.connection:
            self.connection.execute(
                "DELETE FROM analyses WHERE id = ?",
                (analysis_id,)
            )

    def close(self):
        self.connection.close()
