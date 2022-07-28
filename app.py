from flask import Flask, request, redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import db_connection, login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
@login_required
def index():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm = request.form.get("confirm")
    if request.method == "POST":
        db = db_connection()
        if db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall():
            return render_template("index.html")
        elif username == "":
            return render_template("index.html")
        elif password == "" or confirm == "" or password != confirm:
            return render_template("index.html")
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, generate_password_hash(password)))
        db.commit()
        db.close()
        return render_template("login.html")
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        db = db_connection()
        if username == "":
            return redirect('/')
        elif password == "":
            return redirect('/')
        user = db.execute("SELECT * FROM users WHERE username= ?", (username,)).fetchone()
        if user is None or not check_password_hash(user[2], password):
            return redirect('/')
        session["user_id"] = user[2]
        db.close()
        return redirect('/')
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run()
