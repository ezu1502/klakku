import os
from flask import Flask, render_template, request, redirect, session
from flask_sock import Sock
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from database import Database
from helpers import validate_register_input

import json

database = Database()

app = Flask(__name__)
sock = Sock(app)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

socket_connections: dict = {}

def get_user_id() -> int | None:
    return session.get("user_id")

def get_username() -> str | None:
    return session.get("username")

@app.get("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirm = request.form.get("confirm-password")

    if not validate_register_input(username, password, confirm):
        return redirect("/register")

    creation_success = database.create_user(username = username, password = password) # type: ignore

    if not creation_success:
        return redirect("/register")

    return redirect("/")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return redirect("/login")

    user_id = database.check_user(username, password)

    if user_id is None:
        return redirect("/login")

    session["user_id"] = user_id
    session["username"] = username

    database.add_login(user_id = user_id)

    return redirect("/")

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chats", methods = ["GET", "POST"])
def chats():
    if request.method == "GET":
        user_id = get_user_id()

        if user_id is None:
            print("user_id is none!")
            return redirect("/")

        user_conversations = database.get_user_conversations(user_id)

        return render_template("chats.html", conversations = user_conversations)

    recipient = request.form.get("username")

    if recipient is None:
        return redirect("/")

    return create_chat(recipient)

def create_chat(recipient_username: str):
    user_id = get_user_id()

    if user_id is None:
        return error()

    result = database.get_user_by_username(recipient_username)

    if result is None:
        print("Recipient doesn't exist!")
        return redirect("/")

    recipient_id = result[0]

    chat_between_users = database.get_chat_between_users(user_id, recipient_id)

    if chat_between_users is None:
        database.create_chat(user_id, recipient_id)
    else:
        print("Chat already exists!")

    return redirect(f"/chat/{recipient_username}")


@app.get("/chat/<recipient_username>")
def chat(recipient_username: str):
    user_id = get_user_id()

    if user_id is None:
        return error()

    result = database.get_user_by_username(recipient_username)

    if result is None:
        return error(code = 404, text = "Couldn't find recipient")

    recipient_id = result[0]

    chat_messages = database.get_chat_messages(user_id, recipient_id)

    if chat_messages is None:
        print("There isn't a chat between the given users!")
        return redirect("/chats")

    chat_messages = [ # (sender_id, content, sent_at)
        {
            "sender_id": message[0],
            "content": message[1],
            "sent_at": datetime.strptime(message[2], "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo = timezone.utc)
            .astimezone(ZoneInfo("America/Sao_Paulo"))
            .strftime("%H:%M")
        }
        for message in chat_messages
    ]

    if any(message["sender_id"] not in (user_id, recipient_id) for message in chat_messages):
        raise RuntimeError("Message does not have a valid sender")
    
    return render_template(
        "chat.html",
        messages = chat_messages, 
        user = {
            "id": user_id,
            "username": get_username()
        },

        recipient = {
            "id": recipient_id,
            "username": recipient_username
        }
    )

@app.get("/profile/<recipient_username>")
def profile(recipient_username: str):
    user_info = database.get_user_info(recipient_username)

    if user_info is None:
        return redirect("/")

    username = user_info[1]

    info_dict = {
        "messages sent": user_info[2]
    }

    return render_template("profile.html", username = username, user_info = info_dict)

@sock.route("/ws")
def websocket(ws):
    user_id = get_user_id()
    if user_id is None:
        ws.close()
        return
    
    socket_connections[user_id] = ws
    # print(f"CONNECTED: user={user_id}, connections={list(socket_connections.keys())}")

    try:
        while True:
            message = ws.receive()

            if message is None:
                break

            message_object = json.loads(message)
            message_object["user_id"] = user_id

            message_object["timestamp"] = (
                datetime.now(timezone.utc).isoformat()                          
            )

            echo_message = json.dumps(message_object)

            recipient_id = int(message_object["recipient_id"])
            chat_id = database.get_chat_between_users(user_id, recipient_id)

            if chat_id is None:
                # Depois posso criar uma função que já cria o chat entre eles se n houver
                continue

            database.add_message(user_id, chat_id, message_object["content"])
            if recipient_id in socket_connections:
                socket_connections[recipient_id].send(echo_message)


            ws.send(echo_message)
    finally:
        if socket_connections.get(user_id) is ws:
            del socket_connections[user_id]

            # print(f"DISCONNECTED: user={user_id}, connections={list(socket_connections.keys())}")



def error(code: int = 400, text: str = "Something went wrong"):
    return render_template("error.html", code = code, text = text)


if __name__ == "__main__":
    app.run(debug = True)
    # app.run()
    # app.run(host = "0.0.0.0")