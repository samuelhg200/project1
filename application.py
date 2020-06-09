import os
import requests

from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from help import login_required

app = Flask(__name__)
API_KEY = "6w569cwH9fLUjf2I6z3Ww"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@login_required
@app.route("/")
def index():
    return redirect("/login")

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
        db.commit()
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

    db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {"username": username, "hash": generate_password_hash(password)})
    db.commit()

    return redirect("/login")
    
