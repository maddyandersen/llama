# Team llama (Maddy Andersen, Amelia Chin, Ari Schechter, Liam Kronman)
# SoftDev -- Rona Ed.
# P5 - Twitter Madlibs
# 2021 - 06 - 14

from flask import Flask, render_template, session, request, redirect, url_for

import sqlite3
import os
import random
import urllib
import json

app = Flask(__name__)
app.secret_key = os.urandom(32)
dir = os.path.dirname(__file__) or "."
dir += "/"

DB_FILE = "twittermad.db"

'''
def create_tables():
    command = "CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT);"
    command += "CREATE TABLE IF NOT EXISTS tweets(tweet_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, content TEXT);"
    c.executescript(command)
    db.commit()
'''

'''
fail safe!
'''
def random_error():
    return render_template("error.html", message="Something went wrong.")


'''
root landing page
'''
@app.route("/")
def index():
    if 'username' in session:
        return home()
    return render_template("first.html")


'''
logout function
'''
@app.route("/logout")
def logout():
    try:
        session.pop('username')
        #session.pop('user_id')
        return redirect("/")
    except:
        return render_template("error.html")

'''
function that specifically handles case that either user has attempted login with
invalid credentials or that new user tried to register with username that was already taken.
uses positional arguments to be called from within multiple functions with same use case.
'''
def auth_error(is_user_conflict=False, is_login_incorrect=False):
    if is_user_conflict:
        return render_template("signup.html", message="Username Already Exists.")
    if is_login_incorrect:
        return render_template("login.html", message="Username or Password is Incorrect.")


'''
all content contained on main user page within this function
'''
@app.route("/home")
def home():
    try:
        # db stuff to get all users' tweets
        print(session['user_id'])
        return render_template("home.html")
    except:
        return random_error()


@app.route("/login")
def login():
    return render_template("login.html")


'''
login function
'''
@app.route("/loginRequest", methods=["POST"])
def loginRequest():
    try:
        # based on form, have form.request['elem'] tags here
        username = request.form["username"]
        password = request.form["password"]

        db = sqlite3.connect(dir + DB_FILE) # dir + "blog.db") # connects to sqlite table
        c = db.cursor()

        # make a list of the password and user_id where the username matches given
        c.execute("SELECT password, user_id FROM users WHERE username=?", (username,))
        accounts = list(c) #returns tuple
        # so if username does not exist, list will be empty and len(accounts) = 0
        # OR if password entered does not match password on file
        if len(accounts) == 0 or password != accounts[0][0]:
            # returns error saying "Username or Password is Incorrect."
            return auth_error(is_login_incorrect=True)
        else:
            # add user and user_id to session for auth purposes
            session['username'] = username
            session['user_id'] = accounts[0][1]
        return redirect("/")
    except:
        return random_error()


'''
function to load signup.html page where users can register using form as opposed to logging in
'''
@app.route("/signup")
def signup():
    return render_template("signup.html")


'''
helper function, used in register
'''
def convert(arr: list) -> list:
    return [list(item) for item in arr]


'''
register function, registers new users
'''
@app.route("/signupRequest", methods=["POST"])
def signupRequest():
        username = request.form["username"]
        password = request.form["password"]

        db = sqlite3.connect(dir + DB_FILE) # dir + "blog.db") # connects to sqlite table
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL);")
        # c.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        c.execute("SELECT username FROM users;")

        pre_existing_usernames = convert(list(c))

        # if username has already been taken
        if [username] in pre_existing_usernames:
            # return error saying "Username Already Exists."
            return auth_error(is_user_conflict=True)
        else:
            c.execute("INSERT INTO users (user_id, username, password) VALUES (NULL, ?, ?)", (username, password))
            db.commit()

            # make a list of the password and user_id where the username matches given
            c.execute("SELECT password, user_id FROM users WHERE username=?", (username,))
            accounts = list(c) #returns tuple
            # add user and user_id to session for auth purposes
            session['username'] = username
            session['user_id'] = accounts[0][1]
            return home()


if __name__ == '__main__':
    app.debug = True
    app.run()
