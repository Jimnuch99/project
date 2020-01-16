import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session.get("user_id")
    # Get stocks of current user
    stocks = db.execute("SELECT * FROM stocks WHERE user_id = :user_id", user_id=user_id)
    # look up for every stock to check name and price
    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = quote["price"] * stock["shares"]
    # get cash from current user
    rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
    cash = rows[0]["cash"]
    # make sum of stocks and cash
    total = sum(stock["total"] for stock in stocks) + cash

    for stock in stocks:
        stock["price"] = usd(stock["price"])
        stock["total"] = usd(stock["total"])

    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol_input = request.form.get("symbol")
        shares_input = request.form.get("shares")

        if not symbol_input or not lookup(symbol_input):
            return apology("Invalid symbol", 400)

        try:
            shares = int(shares_input)
        except ValueError:
            return apology("Shares is not an integer", 400)

        if shares <= 0:
            return apology("Shares is not a positive integer", 400)

        user_id = session.get("user_id")
        quote = lookup(symbol_input)
        price = quote["price"] * shares
        # get cash from current user
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = rows[0]["cash"]
        if price > cash:
            return apology("You cannot afford this", 400)

        # update cash
        cash = cash - price
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id",
                    cash=cash, user_id=user_id)

        # add purchase to db
        db.execute("INSERT INTO transactions (user_id, symbol, shares, cash_change) VALUES (:user_id, :symbol, :shares, :cash_change)",
                   user_id=user_id, symbol=symbol_input, shares=shares, cash_change=-price)

        # update stocks in db
        rows = db.execute("SELECT shares FROM stocks WHERE user_id = :user_id AND symbol = :symbol",
                          user_id=user_id, symbol=symbol_input)
        # if row does not exist make new one, else update row
        if len(rows) == 0:
            db.execute("INSERT INTO stocks (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                       user_id=user_id, symbol=symbol_input, shares=shares)
        else:
            total_shares = rows[0]["shares"] + shares
            db.execute("UPDATE stocks SET shares = :shares WHERE user_id = :user_id AND symbol = :symbol",
                       shares=total_shares, user_id=user_id, symbol=symbol_input)

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username_input = request.args.get("username")

    if not username_input:
        return jsonify(False)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username = username_input)

    if len(rows) == 1:
        return jsonify(False)

    return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session.get("user_id")
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = :user_id", user_id=user_id)

    for transaction in transactions:
        transaction["cash_change"] = usd(transaction["cash_change"])

    return render_template("history.html", transactions=transactions)


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
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        symbol_input = request.form.get("symbol")

        if not symbol_input:
            return apology("Enter a symbol", 400)

        rows = lookup(symbol_input)

        if not rows:
            return apology("Invalid Symbol", 400)

        rows["price"] = usd(rows["price"])

        return render_template("quoted.html", rows=rows)

    else:
        return render_template("quote.html")

#registered students

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username_input = request.form.get("username")
        password_input = request.form.get("password")

        # Ensure username was submitted
        if not username_input:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password_input:
            return apology("must provide password", 400)

        elif password_input != request.form.get("confirmation"):
            return apology("must provide 1 password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = username_input)

        if len(rows) == 1:
            return apology("username already exists", 400)

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :Passwordhash)",
        username = username_input, Passwordhash=generate_password_hash(password_input, method ='pbkdf2:sha256', salt_length=8))

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol_input = request.form.get("symbol")
        shares_input = request.form.get("shares")

        if not symbol_input or not lookup(symbol_input):
            return apology("Invalid symbol", 400)

        try:
            shares = int(shares_input)
        except ValueError:
            return apology("Shares is not an integer", 400)

        if shares <= 0:
            return apology("Shares is not a positive integer", 400)

        user_id = session.get("user_id")
        quote = lookup(symbol_input)
        price = quote["price"] * shares
        # check how many shares a user has of a certain stock
        rows = db.execute("SELECT shares FROM stocks WHERE user_id = :user_id AND symbol = :symbol",
                          user_id=user_id, symbol=symbol_input)

        if len(rows) == 0 or rows[0]["shares"] < shares:
            return apology("Insufficient shares", 400)

        # Update owned shares.
        total_shares = rows[0]["shares"] - shares
        db.execute("UPDATE stocks SET shares = :shares WHERE user_id = :user_id AND symbol = :symbol",
                   shares=total_shares, user_id=user_id, symbol=symbol_input)

        # Update cash.
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = rows[0]["cash"] + price
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id",
                   cash=cash, user_id=user_id)

        # Add transaction.
        db.execute("INSERT INTO transactions (user_id, symbol, shares, cash_change) VALUES (:user_id, :symbol, :shares, :cash_change)",
                   user_id=user_id, symbol=symbol_input, shares=-shares, cash_change=price)



        return redirect("/")
    else:
        user_id = session.get("user_id")
        rows = db.execute("SELECT symbol FROM stocks WHERE user_id = :user_id", user_id=user_id)
        symbols = [row["symbol"] for row in rows]
        return render_template("sell.html", symbols=symbols)


@app.route("/add-funds", methods=["GET", "POST"])
@login_required
def add_funds():
    """Add funds to a user's account"""
    if request.method == "POST":
        cash_input = request.form.get("cash")
        user_id = session.get("user_id")

        cash_to_add = float(cash_input)
        if cash_to_add <= 0:
            return apology("Cash must be a positive number", 400)

        # Update cash
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = rows[0]["cash"] + cash_to_add
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id",
                   cash=cash, user_id=user_id)

        return redirect("/")
    else:
        return render_template("add_funds.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
