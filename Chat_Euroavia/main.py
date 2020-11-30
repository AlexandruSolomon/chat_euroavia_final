import os

from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'euroavia'
db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins='*')


class Messages(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    msg = db.Column(db.String(280))

    def __init__(self, user, text):
        self.username = user
        self.msg = text


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form["nickname"]
        session["user"] = user
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/", methods=["POST", "GET"])
def home():
    if "user" in session:
        all_texts = Messages.query.all()

        user = session["user"]

        if request.method == "POST":
            msg_text = request.form["message"]
            if msg_text != "":
                new_text = Messages(user, msg_text)
                db.session.add(new_text)
                db.session.commit()

                return redirect(url_for("home"))

        return render_template("home.html", user=user, messages=all_texts)
    else:
        return redirect(url_for("login"))


@socketio.on('message')
def message(data):
    if data['msg'] != '':
        new_text = Messages(data['username'], data['msg'])
        db.session.add(new_text)
        db.session.commit()
        send({'msg': data['msg'], 'username': data['username']}, broadcast=True)


if __name__ == "__main__":
    db.create_all()
    socketio.run(app, debug=True)
