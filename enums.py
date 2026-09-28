from enum import Enum
from pathlib import Path

COMMAND_FOLDER = Path(__file__).parent / "sql_commands"

class SQLCommands(Enum):
    SCHEMA = COMMAND_FOLDER / "schema.sql"

    CREATE_USER = COMMAND_FOLDER / "create_user.sql"
    CHECK_USER = COMMAND_FOLDER / "check_user.sql"
    GET_USER_BY_USERNAME = COMMAND_FOLDER / "get_user_by_username.sql"

    GET_CONVERSATION = COMMAND_FOLDER / "get_conversation.sql"
    GET_USER_CONVERSATIONS = COMMAND_FOLDER / "get_user_conversations.sql"

    ADD_LOGIN = COMMAND_FOLDER / "add_login.sql"