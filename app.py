from cs50 import SQL
from flask import Flask, redirect, render_template, session, request, url_for, abort
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

def get_user_rows(email):
    return db.execute("SELECT * FROM users WHERE email = ?", email)

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user[0]["username"].capitalize()

    return render_template("index.html", username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return abort(403, description="Must provide email")
        # print("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return abort(403, description="Must provide password")
        # print("must provide password", 403)

        # Query database for username
        rows = get_user_rows(request.form.get("email"))

        print(rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return abort(403, description="Invalid username and/or password")
        # print("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

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

        # Add validation for the email
        email = request.form.get("email")
        if not email:
            return print("Please input a email")

        rows = get_user_rows(email)

        # Ensure username does not exists already
        if len(rows) == 1:
            return print("User already exists")

        # Add validation for the password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation:
            return print("Please fill up both fields")

        if password != confirmation:
            return print("Both passwords must be the same")

        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hashed_password)

        # Query database for the new username
        rows = get_user_rows(email)
        print(rows)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
