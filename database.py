import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager
from enums import SQLCommands

class Database:
    def __init__(self) -> None:
        self.initialize_database()

    def read_command(self, command: SQLCommands):
        command_text = command.value.read_text(encoding = "utf-8")

        if not command_text:
            raise RuntimeError("Couldn't read command")

        return command_text

    def _get_connection(self):
        con = sqlite3.connect("klakku.db")
        con.execute("PRAGMA foreign_keys = ON")
        return con

    @contextmanager
    def connection(self, *, commit: bool = True):
        connection = self._get_connection()
        try:
            yield connection

            if commit:
                connection.commit()
        except:
            connection.rollback()
            raise
        finally:
            connection.close()

    def execute_sql(self, code: str, arguments: tuple | None = None):
        with self.connection() as con:
            if arguments is not None:
                con.execute(code, arguments)
            else:
                con.execute(code)


    def initialize_database(self):
        with self.connection() as con:
            con.executescript(self.read_command(SQLCommands.SCHEMA))

    def create_user(self, username: str, password: str) -> bool:
        try:
            password_hash = generate_password_hash(password)

            self.execute_sql(
                self.read_command(SQLCommands.CREATE_USER),
                (username, password_hash)
            )

            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, username: str, password: str) -> int | None:
        with self.connection(commit = False) as con:
            result = con.execute(
                self.read_command(SQLCommands.CHECK_USER),
                (username,)
            ).fetchone()

            if result is None:
                return None

            user_id, password_hash = result

            if not check_password_hash(password_hash, password):
                return None


            return int(user_id)

    def get_user_by_username(self, username: str) -> tuple[int, str] | None:
        """
            Receives a username and returns a tuple in the format (user_id, username).
        """
        with self.connection(commit = False) as con:
            user = con.execute(self.read_command(SQLCommands.GET_USER_BY_USERNAME), (username,)).fetchone()

            if user is None:
                return None

            return user

    def get_conversation_with_user_ids(self, id_1: int, id_2: int) -> int | None:
        with self.connection(commit = False) as con:
            conversation = con.execute(self.read_command(SQLCommands.GET_CONVERSATION), (id_1, id_2)).fetchone()

            if conversation is None:
                return None

            return int(conversation[0])
            
    def get_user_conversations(self, user_id: int) -> list[tuple[int, str]]:
        """ 
            Receives a user_id and returns a list containing (conversation_id, other_username) pairs
            for the given user.
        """

        with self.connection(commit = False) as con:
            conversations = con.execute(
                self.read_command(SQLCommands.GET_USER_CONVERSATIONS),
                (user_id, user_id)
            ).fetchall()

            return conversations

    def add_login(self, user_id: int) -> None:
        """ 
            Inserts a new login record into the database.
        """
        with self.connection() as con:
            con.execute(
                self.read_command(SQLCommands.ADD_LOGIN),
                (user_id,)
            )

            
            
