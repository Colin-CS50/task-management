from cs50 import SQL
from flask import Flask, redirect, render_template, session, request, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///task.db")

def get_user_rows(username):
    return db.execute("SELECT * FROM users WHERE username = ?", username)

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user[0]["username"].capitalize()

    return render_template("index.html", username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Add validation for the username
        username = request.form.get("username")
        if not username:
            return print("Please input a username")

        rows = get_user_rows(username)

        # Ensure username does not exists already
        # if len(rows) == 1:
        #     return print("User already exists")

        # Add validation for the password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation:
            return print("Please fill up both fields")

        if password != confirmation:
            return print("Both passwords must be the same")

        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

        # Query database for the new username
        rows = get_user_rows(username)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
