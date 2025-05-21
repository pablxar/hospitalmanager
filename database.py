import sqlite3

class DatabaseManager:
    def __init__(self, db_name="app_data.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    file_content BLOB NOT NULL
                )
                """
            )

    def insert_analysis(self, name, date, file_content):
        with self.connection:
            self.connection.execute(
                "INSERT INTO analyses (name, date, file_content) VALUES (?, ?, ?)",
                (name, date, file_content)
            )

    def fetch_analyses(self):
        with self.connection:
            return self.connection.execute("SELECT * FROM analyses").fetchall()

    def close(self):
        self.connection.close()
