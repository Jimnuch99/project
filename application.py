import os
import urllib,json
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required

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
api_key = "SFc7YRbTLzNil5YjMQyFhFI2y66KptWm"

# @app.route("/personalfeed", methods =["GET", "POST"])
# @login_required
# def personalfeed():
#     return render_template("personalfeed.html")

@app.route("/", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect('/')

        # ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/")

        elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', request.form.get("password")):
         # no match
            flash("Passwords don't match")
            return redirect('/')

            #return apology("Password must contain at least 8 characters, one uppercase letter, one special character and one number")

        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match")
            return redirect('/')

        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users (username, hash) \
                             VALUES(:username, :hash)", \
                             username=request.form.get("username"), \
                             hash=generate_password_hash(request.form.get("password")))

        if not result:
            flash("Username already exist")
            return redirect("/")

        session["user_id"] = result
        flash("Registration succesful")

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
            flash("Must provide username")
            return redirect('/login')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect('/login')

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Combination of username and password doesn't exist")
            return redirect('/login')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        naam = db.execute("SELECT username FROM users WHERE id=:user_id", user_id=session['user_id'])
        session['username'] = naam[0]['username']

        # Redirect user to home page
        return redirect("/feed")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/feed")
@login_required
def feed():
    rows = db.execute("SELECT url, username, memes.id FROM memes, users WHERE memes.user_id = users.id ORDER BY timestamp DESC LIMIT 20")
    return render_template("feed.html", memes=rows)

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        search_term = request.form.get("search")

        url = 'http://api.giphy.com/v1/gifs/search'
        values = { 'q': search_term, 'apiKey': api_key, 'limit': 20 }

        response=json.loads(urllib.request.urlopen(url + '?' + urllib.parse.urlencode(values)).read())

        return render_template("searchresults.html", results=response["data"])
    else:
        return render_template("post.html")

@app.route("/postmeme", methods=["POST"])
@login_required
def postmeme():
    user_id = session.get("user_id")
    url = request.form.get("embed_url")
    result = db.execute("INSERT INTO memes (user_id, url) \
                         VALUES(:user_id, :url)",
                         user_id=user_id,
                         url=url)
    return redirect("/feed")

@app.route("/account")
@login_required
def account():
    rows = db.execute("SELECT url FROM memes WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 20", user_id=session["user_id"])
    print(rows)
    return render_template("account.html", memes=rows)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search")
        rows = db.execute("SELECT id, username FROM users WHERE username LIKE %s", ("%" + search_term + "%",))
        for row in rows:
            print(row)
        return render_template("userresults.html", results=rows)
    else:
        return render_template("search.html")

# @app.route("/followUser")
# @login_required
# def followuser():
#     user_id = self.request.get("userId")
#     print(user_id)
#     return user_id

@app.route("/savememe", methods=["POST"])
@login_required
def savememe():
    user_id = session.get("user_id")
    meme_id = request.form.get("meme_id")
    result = db.execute("INSERT INTO savedmemes (user_id, meme_id) \
                         VALUES(:user_id, :meme_id)",
                         user_id=user_id,
                         meme_id=meme_id)
    return redirect("/feed")

@app.route("/savedmemes")
@login_required
def savedmemes():
    rows = db.execute("SELECT url FROM savedmemes, memes WHERE savedmemes.meme_id = memes.id AND savedmemes.user_id = :user_id ORDER BY timestamp DESC LIMIT 20", user_id=session["user_id"])
    print(rows)
    return render_template("savedmemes.html", memes=rows)

@app.route("/followuser")
@login_required
def followuser():
    user_id = session.get("user_id")
    user_id2 = request.form.get("user_id2")
    result = db.execute("INSERT INTO followedusers (user_id, user_id2) \
                         VALUES(:user_id, :user_id2)",
                         user_id=user_id,
                         user_id2=user_id2)
    return redirect("/feed")

@app.route("/personalfeed")
@login_required
def personalfeed():
    rows = db.execute("SELECT user_id2 FROM followedusers, memes WHERE followedusers.user_id2 = user_id2 AND followedusers.user_id2 = :user_id", user_id=session["user_id"])
    print(rows)
    return render_template("personalfeed.html", followedusers=rows)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



