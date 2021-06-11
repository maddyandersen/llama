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
import requests
import nltk

app = Flask(__name__)
app.secret_key = os.urandom(32)
dir = os.path.dirname(__file__) or "."
dir += "/"

DB_FILE = "twittermad.db"

BEARER_TOKEN = open("keys/key_twitter.txt", "r").read().split()[2]
SPACHE_WORDS = open("keys/spache_words.txt", "r").read().split()

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
        session.pop('user_id')
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
        db = sqlite3.connect(dir + DB_FILE) # connects to sqlite table
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tweets(tweet_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT NOT NULL, link TEXT NOT NULL);")
        #c.execute("INSERT INTO tweets(tweet_id, user_id, content) VALUES (NULL, ?, ?)", (3, "I like dogs"))
        #.execute("INSERT INTO tweets(tweet_id, user_id, content) VALUES (NULL, ?, ?)", (3, "I like cats"))

        # make a list of all the tweet_ids, user_ids, and tweet content
        c.execute("SELECT * FROM tweets")
        tweets = list(c)

        allTweets = []

        for row in tweets:
            c.execute("SELECT username FROM users WHERE user_id=?", (row[1],))
            name = list(c)
            allTweets.append((name[0][0], row[2], row[3]))

        return render_template("home.html", tweets = allTweets)
    except:
        return random_error()


'''
all content contained on profile page within this function
'''
@app.route("/myTweets")
def myTweets():
    try:
        db = sqlite3.connect(dir + DB_FILE) # connects to sqlite table
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tweets(tweet_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT NOT NULL, link TEXT NOT NULL);")

        #c.execute("INSERT INTO tweets(tweet_id, user_id, content) VALUES (NULL, ?, ?)", (3, "I like dogs"))
        #c.execute("INSERT INTO tweets(tweet_id, user_id, content) VALUES (NULL, ?, ?)", (3, "I like cats"))

        # make a list of all the tweet content for this user
        c.execute("SELECT content, link FROM tweets WHERE user_id=?", (session.get("user_id"),))
        tweets = list(c)
        c.execute("SELECT username FROM users WHERE user_id=?", (session.get("user_id"),))
        name = list(c)

        myTweets = []

        for row in tweets:
            myTweets.append((row[0], row[1]))

        return render_template("profile.html", username = name[0][0], tweets = myTweets)
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
    #try:
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
    #except:
        #return random_error()


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


@app.route("/tweet")
def createTweet():
    randWord = random.choice(SPACHE_WORDS)
    print(randWord)
    all_headers =  {
        "Authorization": "Bearer " + BEARER_TOKEN,
        "User-Agent": "p5-llama"
    }

    request_params = {
        'q': randWord,
        'count': 100,
        'lang': 'en',
        'tweet_mode': 'extended'
    }

    resp = requests.get('https://api.twitter.com/1.1/search/tweets.json', params=request_params, headers=all_headers).json()
    link = "https://twitter.com/_/status/" + str(resp["statuses"][0]["id"])

    try:
        text = resp["statuses"][0]["retweeted_status"]['full_text']
        print(text)
    except:
        text = resp["statuses"][0]['full_text']
    text = text.lower()
    parsed_text = parse_text(text)
    return tweetForm(parsed_text, int(0.30 * len(parsed_text)), link)

def tweetForm(text, change_len, link):
    chosen = random.choice(text)
    while chosen[1] != 'CD' and chosen[1] != 'JJ' and chosen[1] != 'N' and chosen[1] != 'JJR' and chosen[1] != 'JJS' and chosen[1] != 'MD' and chosen[1] != 'NN' and chosen[1] != 'NNP' and chosen[1] != 'NNS' and chosen[1] != 'PRP' and chosen[1] != 'PRP$' and chosen[1] != 'RB' and chosen[1] != 'RBR' and chosen[1] != 'UH' and chosen[1] != 'VB' and chosen[1] != 'VBD' and chosen[1] != 'VBG' and chosen[1] != 'VBN' and chosen[1] != 'VBP' and chosen[1] != 'VBZ':
        chosen = random.choice(text)
    location = text.index(chosen)
    typeChange = chosen[1]
    return render_template("create_tweet.html", text=text, index=location, type=typeChange, count=change_len, link=link)


@app.route("/tweetRequest", methods=["POST"])
def changeTweet():
    text = request.form["text"]
    parse_text = []
    elements = text[2:-3].split("), (")
    for element in elements:
        tmp = element.split(", ")
        new_tmp = []
        for el in tmp:
            if el.index('\\') >= 0:
              el.replace('\\', '')
            if el == "'":
                new_tmp.append("'", 'POS')
            elif el[0] != "'" and el[-1] != "'":
                new_tmp.append(el)
            elif el[0] != "'" and el[-1] == "'":
                new_tmp.append(el[0:-1])
            elif el[0] == "'" and el[-1] != "'":
                new_tmp.append(el[1::])
            else:
                new_tmp.append(el[1:-1])
        if new_tmp[0] == ".',":
            tuple = (".", "PDT")
        else:
            try:
                tuple = (new_tmp[0], new_tmp[1])
            except:
                tuple = (new_tmp[0][0:-3], "")
        parse_text.append(tuple)
    text = parse_text
    index = int(request.form["index"])
    word = request.form["word"]
    count = int(request.form["count"])
    link = request.form["link"]
    if count > 0:
        text[index] = (word, text[index][1])
        count -= 1
        return tweetForm(text, count)
    db = sqlite3.connect(dir + DB_FILE) # connects to sqlite table
    c = db.cursor()
    # c.execute("CREATE TABLE IF NOT EXISTS tweets(tweet_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT NOT NULL);")
    output_text = []
    for tuple in text:
        output_text.append(tuple[0])
    finalTweet = " ".join(output_text)
    print(finalTweet)
    print(session.get("user_id"))
    c.execute("INSERT INTO tweets(tweet_id, user_id, content, link) VALUES (NULL, ?, ?, ?)", (session.get("user_id"), finalTweet, link))
    db.commit()
    c.execute("SELECT * FROM tweets")
    accounts = list(c)
    print(accounts)
    return redirect(url_for('myTweets'))


def parse_text(text):
   tokenized = nltk.word_tokenize(text)
   parsed = nltk.pos_tag(tokenized)
   return parsed


if __name__ == '__main__':
    app.debug = True
    app.run()
