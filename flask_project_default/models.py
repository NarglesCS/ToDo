from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(180))
    name = db.Column(db.String(40))


class ToDO(db.Model):
     id = db.Column(db.Integer, primary_key = True)
     username_id = db.Column(db.String(40))
     task = db.Column(db.String(256))
     due_date= db.Column(db.DateTime)
     position = db.Column(db.Integer)
     complete = db.Column(db.Boolean)

     def __init__(self, user_id, tsk, due, pos = 1, completed = False):
         self.username_id = user_id
         self.task = tsk
         self.due_date = due
         self.position = pos
         self.complete = completed
