import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["IMAGE_UPLOADS"] = "/mnt/c/wsl/projects/pythonise/tutorials/flask_series/app/app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///meme.db")


@app.route("/", methods=["GET", "POST"])
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

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    """Register user"""

    if request.method == "POST":

        #vraag de velden in de register.html op
        gebruikersnaam = request.form.get('username')
        wachtwoord = request.form.get('password')
        dubbelcheck = request.form.get('confirmation')
        wachtwoordhash = generate_password_hash(wachtwoord)

        #de foutmeldingen wanneer een van de velden niet is ingevoerd
        if not gebruikersnaam:
            return apology("Voer een gebruikersnaam in")

        elif not wachtwoord:
            return apology('Voer een wachtwoord in')

        elif not dubbelcheck:
            return apology('Voer een wachtwoord in')

        #geef een foutmelding als de opgegeven wachtwoorden niet overeenkomen
        elif dubbelcheck != wachtwoord:
            return apology('Wachtwoorden komen niet overeen')

        #als alles is goedgegaan, voeg de gebruiker toe in de user-database
        database = db.execute("SELECT * FROM users WHERE username =:username", username = gebruikersnaam)

        if gebruikersnaam in database:
            return apology("Gebruikersnaam is al in gebruik")

        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",username=gebruikersnaam, hash=wachtwoordhash)

        #session["user_id"] = goedgekeurd
        flash("Welkom bij memestagram!")
        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
