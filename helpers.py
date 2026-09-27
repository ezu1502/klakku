import re as regex

def validate_register_input(username, password, confirm) -> bool:
    filled = bool(username and password and confirm) and password == confirm
    
    if not filled:
        return False

    if not regex.fullmatch(r"(?=.*[a-zA-Z])[a-zA-Z0-9_]{3,15}", username):
        return False

    if len(password) < 5:
        return False

    print("validou")
    return True

    