import os
import requests

from flask import Flask, session, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp

from help import login_required

app = Flask(__name__)
API_KEY = "6w569cwH9fLUjf2I6z3Ww"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure responses aren't cached in server
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate,  public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return redirect("/search")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    #get user info, return error if failed
    user = db.execute("SELECT id, hash FROM users WHERE username = :username", {"username": username}).fetchone()
    if not user:
        return "ERROR"

    #check if password is correct --> if correct let in, else error
    if check_password_hash(user.hash, password):
        session["user_id"] = user.id
        return redirect("/")
    else:
        return "Incorrect password"



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    #insert info into table users
    db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {"username": username, "hash": generate_password_hash(password)})
    db.commit()

    return redirect("/login")

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return render_template("search.html")
    
    keyword = request.form.get('keyword')

    if not keyword:
        return redirect(url_for('booksearch', keyword= ""))

    return redirect(url_for('lookup', keyword=keyword))



@app.route("/search/<string:keyword>")
@login_required
def lookup(keyword):


    books = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn ILIKE :keyword OR title ILIKE :keyword OR author ILIKE :keyword", {"keyword": "%" + keyword + "%"}).fetchall()

    return render_template("booklist.html", books=books)


   
