import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///meme.db")

@app.route("/", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password")

        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password doesn't match")

        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users (username, hash) \
                             VALUES(:username, :hash)", \
                             username=request.form.get("username"), \
                             hash=generate_password_hash(request.form.get("password")))

        if not result:
            return apology("Username already exist")

        # remember which user has logged in
        session["user_id"] = result

        # redirect user to home page
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("feed")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/feed")
@login_required
def feed():
    return render_template("feed.html")

@app.route("/post")
@login_required
def post():
    return render_template("post.html")

@app.route("/account")
@login_required
def account():
    return render_template("account.html")

@app.route("/search")
@login_required
def search():
    return render_template("search.html")

@app.route("/savedmemes")
@login_required
def savedmemes():
    return render_template("savedmemes.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
