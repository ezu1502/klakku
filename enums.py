from enum import Enum, auto
from pathlib import Path

COMMAND_FOLDER = Path(__file__).parent / "sql_commands"

class SQLCommands(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name.lower() + ".sql"

    SCHEMA = auto()

    CREATE_USER = auto()
    CHECK_USER = auto()
    GET_USER_BY_USERNAME = auto()
    GET_USER_INFO = auto()

    GET_CONVERSATION = auto()
    GET_USER_CONVERSATIONS = auto()
    CHECK_CONVERSATION_EXISTS = auto()
    CREATE_CHAT = auto()
    INSERT_CHAT_MEMBER = auto()

    ADD_LOGIN = auto()


    GET_CHAT_MESSAGES = auto()
    ADD_MESSAGE = auto()

    @property
    def path(self) -> Path:
        return COMMAND_FOLDER / self.value