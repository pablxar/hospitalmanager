import sqlite3

class DatabaseManager:
    def __init__(self, db_name="app_data.db"):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

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

    def close(self):
        self.connection.close()
