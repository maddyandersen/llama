import sqlite3

DB_FILE = "twittermad.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

def create_tables(): 
    command = "CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT);"
    command += "CREATE TABLE IF NOT EXISTS tweets(tweet_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, content TEXT);"
    c.executescript(command)
    db.commit()

def checkLogin(username, password):
    command = 'SELECT user_id, username, password FROM users WHERE username = "{}";'.format(
        username)
    info = ()
    for row in c.execute(command):
        info += (row[0], row[1], row[2])
    
    if info[1] == username and info[2] == password:
        return True
    return "Username or password incorrect"

def signUp(username, password):
    command = 'INSERT INTO users VALUES (NULL, "{}", "{}");'.format(username, password)
    c.execute(command)
    db.commit()

def getUserId(username):
    command = 'SELECT user_id FROM users WHERE username = "{}";'.format(username)
    id = 0
    for row in c.execute(command):
        id = row[0]
    return id