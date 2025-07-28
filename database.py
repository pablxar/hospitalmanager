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
                    usuario_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    report BLOB NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

    def update_reports_table(self):
        """Agrega la columna usuario_id a la tabla reports si no existe."""
        with self.connection:
            # Verificar si la columna usuario_id ya existe
            columns = self.connection.execute("PRAGMA table_info(reports)").fetchall()
            column_names = [column[1] for column in columns]
            if "usuario_id" not in column_names:
                self.connection.execute("ALTER TABLE reports ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 1")
                self.connection.execute("PRAGMA foreign_keys = ON")
                self.connection.execute("UPDATE reports SET usuario_id = 1")  # Asignar un valor por defecto
                print("Columna usuario_id agregada a la tabla reports.")

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
            
    def insert_report(self, user_id, analysis_id, content):
        with self.connection:
            self.connection.execute(
                "INSERT INTO reports (usuario_id, name, date, report) VALUES (?, ?, datetime('now'), ?)",
                (user_id, f"Informe de {analysis_id}", content)
            )

    def fetch_analyses_by_user(self, usuario_id):
        with self.connection:
            results = self.connection.execute(
                "SELECT id, name, date, file_content FROM analyses WHERE usuario_id = ? ORDER BY date DESC",
                (usuario_id,)
            ).fetchall()
            # Ensure file_content is returned as bytes
            return [(id, name, date, bytes(file_content)) for id, name, date, file_content in results]

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

    # Reports
    def fetch_reports_by_user(self, usuario_id):
        with self.connection:
            results = self.connection.execute(
                "SELECT id, name, date, report FROM reports WHERE usuario_id = ? ORDER BY date DESC",
                (usuario_id,)
            ).fetchall()
            # Retornar los resultados directamente sin convertir a bytes
            return [(id, name, date, report) for id, name, date, report in results]
    
    def delete_report_by_id(self, report_id):
        with self.connection:
            self.connection.execute(
                "DELETE FROM reports WHERE id = ?",
                (report_id,)
            )

    def close(self):
        self.connection.close()
