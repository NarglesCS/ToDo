from wtforms import Form, BooleanField, StringField, DateTimeField, validators
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=6, max=40)])
    email = StringField('Email Address', [validators.Length(min=6, max=40)])
    name = StringField('Name', [validators.InputRequired()])
    password = StringField('Password', [validators.Length(min=6, max=40)])

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=6, max=40)])
    password = StringField('Password', [validators.Length(min=6, max=40)])

class AddTaskForm(Form):
    task = StringField('Task', [validators.InputRequired()])
    due_date = StringField('Due', [validators.InputRequired()])
