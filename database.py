import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager
from collections.abc import Generator
from enums import SQLCommands as Commands

class Database:
    def __init__(self) -> None:
        self.initialize_database()

    def _read_command(self, command: Commands):
        command_text = command.path.read_text(encoding = "utf-8")

        if not command_text:
            raise RuntimeError("Couldn't read command")

        return command_text

    def _get_connection(self):
        con = sqlite3.connect("klakku.db")
        con.execute("PRAGMA foreign_keys = ON")
        return con

    @contextmanager
    def connection(self, *, commit: bool = True) -> Generator[sqlite3.Connection, None, None]:
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
            con.executescript(self._read_command(Commands.SCHEMA))

    def create_user(self, username: str, password: str) -> bool:
        try:
            password_hash = generate_password_hash(password)

            self.execute_sql(
                self._read_command(Commands.CREATE_USER),
                (username, password_hash)
            )

            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, username: str, password: str) -> int | None:
        with self.connection(commit = False) as con:
            result = con.execute(
                self._read_command(Commands.CHECK_USER),
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
            user = con.execute(self._read_command(Commands.GET_USER_BY_USERNAME), (username,)).fetchone()

            if user is None:
                return None

            return user

    def get_conversation_with_user_ids(self, id_1: int, id_2: int) -> int | None:
        with self.connection(commit = False) as con:
            conversation = con.execute(self._read_command(Commands.GET_CONVERSATION), (id_1, id_2)).fetchone()

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
                self._read_command(Commands.GET_USER_CONVERSATIONS),
                (user_id, user_id)
            ).fetchall()

            return conversations

    def add_login(self, user_id: int) -> None:
        """ 
            Inserts a new login record into the database.
        """
        with self.connection() as con:
            con.execute(
                self._read_command(Commands.ADD_LOGIN),
                (user_id,)
            )

    def get_chat_between_users(self, id_1: int, id_2: int) -> int | None:
        """
            Receives two user ids and returns a conversation id between them if there is any.
            If two users don't have any chat in history, function returns None
        """
        with self.connection(commit = False) as con:
            result = con.execute(
                self._read_command(Commands.CHECK_CONVERSATION_EXISTS),
                (id_1, id_2)
            ).fetchone()    

            return result[0] if result is not None else None
            
            
    def create_chat(self, user_1: int, user_2: int) -> int:
        """
            Creates a new chat between two users and returns its id.
        """

        with self.connection() as con:
            result = con.execute(
                self._read_command(Commands.CREATE_CHAT)
            ).fetchone()

            if result is None:
                raise RuntimeError("Couldn't create chat")

            new_chat_id = result[0]

            print("user_1:", user_1)
            print("user_2:", user_2)
            print("new_chat_id:", new_chat_id)

            print(
                "users:",
                con.execute("SELECT id, username FROM users").fetchall()
            )

            print(
                "conversations:",
                con.execute("SELECT id FROM conversations").fetchall()
            )

            con.execute(
                self._read_command(Commands.INSERT_CHAT_MEMBER),
                (new_chat_id, user_1)
            )

            con.execute(
                self._read_command(Commands.INSERT_CHAT_MEMBER),
                (new_chat_id, user_2)
            )

        return new_chat_id

    def get_chat_messages(self, id_1: int, id_2: int) -> list[tuple] | None:
        """
            Finds the conversation_id between two users and queries the db to return all messages within
            the chat.

            Returns a list of tuples, each message in the following format: (sender_id, content, sent_at) 
        """

        chat_id = self.get_chat_between_users(id_1, id_2)

        if chat_id is None:
            return None

        with self.connection(commit = False) as con:
            result = con.execute(
                self._read_command(Commands.GET_CHAT_MESSAGES),
                (chat_id,)
            ).fetchall()

            return result

    def add_message(self, sender_id: int, conversation_id: int, content: str):
        with self.connection() as con:
            con.execute(
                self._read_command(Commands.ADD_MESSAGE),
                (sender_id, conversation_id, content)
            )

    def get_user_info(self, username: str) -> tuple | None:
        with self.connection(commit = False) as con:
            info = con.execute(
                self._read_command(Commands.GET_USER_INFO),
                (username,)
            ).fetchone()

            if not info:
                return None

            return info