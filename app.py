from cs50 import SQL
from flask import Flask, redirect, render_template, session, request, url_for, abort
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///task.db")

def get_user_rows(email):
    return db.execute("SELECT * FROM users WHERE email = ?", email)


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user[0]["username"].capitalize()
    boards = db.execute("SELECT * FROM boards WHERE user_id = ?", user_id)

    return render_template("index.html", username=username, boards=boards)


@app.route("/board/create", methods=["POST"])
@login_required
def board_create():
    # Ensure name is present
    name = request.form.get("name")
    if not name:
        return abort(403, description="Must provide a name")

    db.execute("INSERT INTO boards (name, user_id) VALUES (?, ?)", name, session["user_id"])
    return redirect("/")


@app.route("/board/<int:id>", methods=["GET"])
@login_required
def board_detail(id):
    board = db.execute("SELECT * FROM boards WHERE id = ? AND user_id = ?", id, session["user_id"])
    columns = db.execute("SELECT * FROM columns WHERE board_id = ? AND board_id IN (SELECT id FROM boards WHERE user_id = ?)", id, session["user_id"])
    if not board:
        return "Board not found or access denied", 404

    return render_template("board.html", board=board[0], columns=columns)


@app.route("/board/<int:id>/delete", methods=["POST"])
def board_delete(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Delete tasks associated with the board and user
    db.execute("DELETE FROM tasks WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?) AND column_id IN (SELECT id FROM columns WHERE board_id IN (SELECT id FROM boards WHERE id = ? AND user_id = ?))", id, id, user_id)

    # Delete columns associated with the board and user
    db.execute("DELETE FROM columns WHERE board_id = ? AND board_id IN (SELECT id FROM boards WHERE id = ? AND user_id = ?)", id, id, user_id)

    # Delete the board
    db.execute("DELETE FROM boards WHERE id = ? AND user_id = ?", id, user_id)

    return redirect("/")


@app.route("/column/create", methods=["POST"])
@login_required
def column_create():
    # Ensure name is present
    board_id = request.form.get("board_id")
    name = request.form.get("name")
    if not name:
        return abort(403, description="Must provide a name")

    db.execute("INSERT INTO columns (name, board_id) VALUES (?, ?)", name, board_id)
    return redirect(url_for('boards', board_id=board_id))


@app.route("/column/<int:column_id>", methods=["GET"])
@login_required
def column_detail(column_id):
    column = db.execute("SELECT * FROM columns WHERE id = ?", column_id)
    if not column:
        return "Column not found or access denied", 404

    return render_template("column.html", column=column[0])


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("email"):
            return abort(403, description="Must provide email")

        elif not request.form.get("password"):
            return abort(403, description="Must provide password")

        rows = get_user_rows(request.form.get("email"))

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return abort(403, description="Invalid username and/or password")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:

        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return print("Please input a username")

        email = request.form.get("email")
        if not email:
            return print("Please input a email")

        rows = get_user_rows(email)

        if len(rows) == 1:
            return print("User already exists")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation:
            return print("Please fill up both fields")

        if password != confirmation:
            return print("Both passwords must be the same")

        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hashed_password)

        rows = get_user_rows(email)
        print(rows)
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
