from flask import Flask, render_template, request, redirect

from database import Database
from helpers import validate_register_input

database = Database()
app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug = True)