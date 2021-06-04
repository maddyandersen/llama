from flask import Flask, render_template, session, request, redirect
from db_manager import *
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

create_tables()

@app.route("/")
def index():
    if 'username' in session:
        return render_template("home.html")
    return render_template("first.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signupRequest", methods=["POST"])
def signupRequest():
    name = request.form['username']
    passw = request.form['password']
    try:
        signUp(name, passw)
    except sqlite3.IntegrityError:
        return render_template("loginerror.html", error="Username already exists")
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/loginRequest", methods=["POST"])
def loginRequest():
    name = request.form['username']
    passw = request.form['password']
    response = checkLogin(name, passw)
    if response:
        session['user_id'] = getUserId(name)
        session['username'] = name
        return redirect("/")
    return render_template("loginerror.html", error=response)


@app.route("/logout")
def logout():
    session.pop('username')
    session.pop('user_id')
    return redirect("/")


if __name__ == "__main__":
    app.debug = True
    app.run()