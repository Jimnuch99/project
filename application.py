import os
import urllib,json
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import InternalServerError
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

@app.route("/", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect('/')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/")

        elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', request.form.get("password")):
         # No match
            flash("Passwords don't match")
            return redirect('/')

        # Ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match")
            return redirect('/')

        # Insert the new user into users, storing the hash of the user's password
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
    # Show all posts out of the database
    rows = db.execute("SELECT url, username, memes.id FROM memes, users WHERE memes.user_id = users.id ORDER BY timestamp DESC LIMIT 20")
    return render_template("feed.html", memes=rows)

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":

        # Search trough the API with the search term
        search_term = request.form.get("search")

        url = 'http://api.giphy.com/v1/gifs/search'
        values = { 'q': search_term, 'apiKey': api_key, 'limit': 20 }

        response=json.loads(urllib.request.urlopen(url + '?' + urllib.parse.urlencode(values)).read())

        # Display the search results
        return render_template("searchresults.html", results=response["data"])
    else:
        return render_template("post.html")

@app.route("/postmeme", methods=["POST"])
@login_required
def postmeme():

    # Post the chosen meme from 'post'
    user_id = session.get("user_id")
    url = request.form.get("embed_url")

    # Insert the url from the chosen meme into the database
    result = db.execute("INSERT INTO memes (user_id, url) VALUES(:user_id, :url)", user_id=user_id, url=url)
    flash("Stonks, memelord")
    return redirect("/feed")

@app.route("/account")
@login_required
def account():

    # Show all posts on the personal account page from the logged in user
    rows = db.execute("SELECT url FROM memes WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 20", user_id=session["user_id"])
    print(rows)
    return render_template("account.html", memes=rows)

@app.route("/search", methods=["GET", "POST"])
def search():

    if request.method == "POST":
        # Query the database for the searchterm (search for usernames)
        search_term = request.form.get("search")
        rows = db.execute("SELECT id, username FROM users WHERE username LIKE %s", ("%" + search_term + "%",))
        for row in rows:
            print(row)
        return render_template("userresults.html", results=rows)
    else:
        return render_template("search.html")

@app.route("/followUser", methods=["POST"])
@login_required
def followuser():

    # Ask for the current logged in user
    user_id = session.get("user_id")
    meme_id = request.form.get("meme_id")
    # Select the user_id from the uploader from the meme
    column = db.execute("SELECT user_id FROM memes WHERE id=:meme_id", meme_id=meme_id)
    user_id2 = column[0]["user_id"]
    # Select all memes from the uploader from the meme
    dbquery = db.execute("SELECT * FROM followedusers WHERE user_id=:user_id AND user_id2=:user_id2", user_id=user_id, user_id2=user_id2)

    # If the logged in users wants to follom him or herself
    if user_id == user_id2:
        flash("It isn't possible to follow yourself")
        return redirect("/feed")

    # If the logged in user already follows the user he/she wants to follow
    elif dbquery:
        flash("You already follow this user")
        return redirect("/feed")

    # Insert the relation into the followedusers table
    else:
        db.execute("INSERT INTO followedusers (user_id, user_id2) VALUES (:user_id, :user_id2)", user_id=user_id, user_id2=column[0]["user_id"])
        flash("Success")

    return redirect("/personalfeed")

@app.route('/unfollowUser', methods=["POST"])
@login_required
def unfollowUser():

    user_id = session.get("user_id")
    meme_id = request.form.get("meme_id")
    column = db.execute("SELECT user_id FROM memes WHERE id=:meme_id", meme_id=meme_id)
    user_id2 = column[0]["user_id"]
    db.execute("DELETE FROM followedusers WHERE user_id=user_id AND user_id2=:user_id2", user_id2=user_id2)

    flash("Did you not like the memes?")

    return redirect("/feed")

@app.route("/personalfeed")
@login_required
def personalfeed():
    user_id = session.get("user_id")
    users = db.execute("SELECT user_id2 FROM followedusers WHERE user_id=:user_id", user_id=user_id)

    if not users:
        flash("You are not following any memelord(s)")
        return redirect("/feed")

    followlist = []
    for x in users:
        db.execute("SELECT url FROM memes WHERE user_id=:user_id", user_id=x["user_id2"])
        followlist.append( db.execute("SELECT url, id FROM memes WHERE user_id=:user_id", user_id=x["user_id2"]))

    return render_template("personalfeed.html", memes=followlist[0])


@app.route("/savememe", methods=["POST"])
@login_required
def savememe():

    # Ask for the current logged in user and ask for the meme_id that the user would like to save
    user_id = session.get("user_id")
    meme_id = request.form.get("meme_id")

    # Query the database and put in in the savedmemes table
    result = db.execute("INSERT INTO savedmemes (user_id, meme_id) \
                         VALUES(:user_id, :meme_id)",
                         user_id=user_id,
                         meme_id=meme_id)

    flash("Meme saved, stonks!")
    return redirect("/savedmemes")

@app.route("/savedmemes")
@login_required
def savedmemes():

    #display all saved memes from the logged in user
    rows = db.execute("SELECT url FROM savedmemes, memes WHERE savedmemes.meme_id = memes.id AND savedmemes.user_id = :user_id ORDER BY timestamp DESC LIMIT 20", user_id=session["user_id"])
    print(rows)
    return render_template("savedmemes.html", memes=rows)

@app.route("/check", methods=["GET"])
def check():
    """ Return true if username available, else false, in JSON format """

    # Get username that the user would like to have
    username = request.form.get("username")

    # Check if username already exists in users
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)

    # return False if the username is unique else True
    if len(rows) != 0 or len(username) == 0:
        return jsonify(False)

    else:
        return jsonify(True)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")



