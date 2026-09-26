import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self) -> None:
        self.initialize_database()

    def _get_connection(self):
        return sqlite3.connect("klakku.db")

    def execute_sql(self, code: str, arguments: tuple | None = None):
        connection = self._get_connection()
        cursor = connection.cursor()

        try:
            if arguments is not None:
                cursor.execute(code, arguments)
            else:
                cursor.execute(code)
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def initialize_database(self):
        self.execute_sql(
        """
            CREATE TABLE IF NOT EXISTS users(
                id integer PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """
        )

    def create_user(self, username: str, password: str) -> bool:
        try:
            password_hash = generate_password_hash(password)

            self.execute_sql(
                """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?);
                """,
                (username, password_hash)
            )

            return True
        except sqlite3.IntegrityError:
            return False

