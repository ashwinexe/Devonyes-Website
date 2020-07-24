import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from datetime import timedelta

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

# db = SQL("postgres://hfdxqepjvbkzzq:35893657093446b6a5ae4ee614d17d9b119522eabf62ed79fe5a785364b206ce@ec2-3-215-83-17.compute-1.amazonaws.com:5432/deeas6g6vusec1")
db = SQL("sqlite:///users.db")
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """
    #Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    
    else:

        if request.form.get("password") == "yearsofexcellence":
            return redirect("/register")


        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Incorrect Username or Password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to index page
        flash("Logged in")
        return redirect("/contents")
        
@app.route("/register", methods=["GET", "POST"])
def register():
    rows = db.execute("SELECT username FROM users WHERE username = :username",
                          username=request.form.get("username"))

    if rows != []:
        flash("Username already taken.")
        return render_template("register.html") 
    # """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")

        if not username:
            flash("You must provide a username.")
            return render_template("register.html") 

        if username in rows:
            flash("Sorry, this username is already taken.")
            return render_template("register.html") 
        password = request.form.get("password")

        if not password:
            flash("You must provide a password.")
            return render_template("register.html") 
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("Password did not match.")
            return render_template("register.html") 

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username=username, password=generate_password_hash(password))
        flash("Welcome!")
        return redirect("/contents")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/contents")
@login_required
def contents():
    return render_template("contents.html")

@app.route("/book")
@login_required
def book():
    return render_template("book.html")

if __name__ == "__main__":
    app.run()