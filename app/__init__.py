from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def index():
    return render_template("layout.html")

if __name__ == "__main__":
    app.debug = True
    app.run()