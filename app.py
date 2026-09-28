import os
from flask import Flask, render_template, request, redirect, session

from database import Database
from helpers import validate_register_input

database = Database()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


def get_user_id():
    return session.get("user_id")

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

    database.add_login(user_id = user_id)

    return redirect("/")

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

def create_chat(rec: str):
    recipient = database.get_user_by_username(rec)

    if recipient is None:
        return redirect("/")

    recipient_id = recipient[0]

    # TODO CHECAR SE JÁ EXISTE UMA CONVERSA ENTRE O USER E O RECIPIENT
    # TODO CRIAR CHAT NO DATABASE
    # TODO REDIRECIONAR PARA CHAT/<RECIPIENT>

    return redirect("/")





@app.get("/chat/<username>")
def chat(username):
    user_id = get_user_id()



    return redirect("/")

def error(code: int = 400, text: str = "Something went wrong"):
    return render_template("error.html", code = code, text = text)


if __name__ == "__main__":
    app.run(debug = True)