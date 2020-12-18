from flask import Flask, redirect, url_for, render_template, request, jsonify, make_response, Response, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, ToDO, User
from forms import SignupForm, LoginForm, AddTaskForm
from datetime import datetime
#from flask import Response as resp

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)
db.create_all()


@app.route('/')
def index():
    '''
    Home page
    '''
    if 'userID' in request.cookies:
        return redirect(url_for('ToDo'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userID' in request.cookies:
        return redirect(url_for('ToDo'))
    else:
        if request.method == "GET":
            form = LoginForm()
            return render_template('login.html', form=form)
        elif request.method == "POST":
            form = LoginForm(request.form)
            if form.validate():
                user = User.query.filter_by(username=form.username.data).first()
                if not user or not check_password_hash(user.password, password = form.password.data):
                    flash('Please check your login details and try again.')
                    return render_template('login.html')
                resp = make_response(redirect(url_for('ToDo')))
                resp.set_cookie('userID', str(user.id))
                return resp
            else:
                flash('Please enter check your login details and try again.')
                return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if 'userID' in request.cookies:
        return redirect(url_for('ToDo'))
    else:
        if request.method == "GET":
            form = SignupForm()
            return render_template('signup.html', form=form)
        elif request.method == "POST":
            form = SignupForm(request.form)
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('Email already exists, please try a different Email.')
                return redirect(url_for('signup'))
            usr_name = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('Username already exists, please try a different Username.')
                return redirect(url_for('signup'))

            new_user = User(email=form.email.data, username=form.username.data, name=form.name.data, password=generate_password_hash(form.password.data, method='sha256'))

            if form.validate():
                db.session.add(new_user)
                db.session.commit()
                resp = make_response(redirect(url_for('ToDo')))
                resp.set_cookie('userID', str(new_user.id))
                return resp
            else:
                flash('Invalid entry please try again.')
                return redirect(url_for('signup'))

@app.route('/logout')
def logout():
    if 'userID' in request.cookies:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('userID')
        return resp
    else:
        return redirect(url_for('index'))

@app.route("/todo", methods=['GET','POST'])
def ToDo():
    if 'userID' in request.cookies:
        ls=[]

        if request.method == "GET":
            todo = ToDO.query.filter_by(username_id=request.cookies['userID']).order_by(ToDO.position.asc())
            form = AddTaskForm()
            if todo:
                for i in todo:
                    ls.append(i.due_date.strftime("%m/%d/%Y"))
                return render_template("todo.html", todo=todo, date=ls, userID=request.cookies['userID'], form=form)
            else:
                return render_template("todo.html", userID=request.cookies['userID'], form=form)

        elif request.method == "POST":
            form = AddTaskForm(request.form)
            if form.validate():
                todo = ToDO.query.filter_by(username_id=request.cookies['userID']).order_by(ToDO.position.desc()).first()
                if todo:
                    new_task = ToDO(request.cookies.get('userID'), form.task.data, datetime.strptime(form.due_date.data, '%Y-%m-%d'), todo.position +1 )
                else:
                    new_task = ToDO(request.cookies.get('userID'), form.task.data, datetime.strptime(form.due_date.data, '%Y-%m-%d'))
                db.session.add(new_task)
                db.session.commit()
                todo = ToDO.query.all()
                for i in todo:
                    ls.append(i.due_date.strftime("%m/%d/%Y"))
                return redirect(url_for('ToDo'))
            else:
                flash("Invalid thing to do")
                return redirect(url_for('ToDo'))
    else:
        return redirect( url_for('login'))

@app.route("/todo/<int:id>/delete", methods=['POST'])
def delete(id):
    u_ID = request.cookies.get('userID')
    if request.method == 'POST':
        to_del = ToDO.query.filter_by(username_id=u_ID, id=id).first()
        pos = to_del.position
        things = ToDO.query.filter_by(username_id=u_ID).order_by(ToDO.position.asc())
        for task in things:
            if task.position >pos:
                task.position -= 1
        db.session.delete(to_del)
        db.session.commit()
    return redirect( url_for('ToDo'))

@app.route("/todo/<int:id>/complete", methods=['POST'])
def complete(id):
    u_ID = request.cookies.get('userID')
    if request.method == 'POST':
        to_complete = ToDO.query.filter_by(username_id=u_ID, id=id).first()
        to_complete.complete = True
        db.session.commit()
        return redirect( url_for('ToDo'))

@app.route("/todo/<int:id>/up", methods=['POST'])
def up(id):
    u_ID = request.cookies.get('userID')
    if request.method == 'POST':
        first_pos = ToDO.query.filter_by(username_id=u_ID).order_by(ToDO.position.asc()).first()
        to_move_up = ToDO.query.filter_by(username_id=u_ID, id=id).first()
        pos_start = to_move_up.position
        if int(id) == int(first_pos.id):
            return redirect( url_for('ToDo'))
        else:
            to_move_up = ToDO.query.filter_by(username_id=u_ID, id=id).first()
            pos_start = to_move_up.position
            to_move_down = ToDO.query.filter_by(username_id=u_ID, position=int(pos_start)-1).first()
            pos_fin = to_move_down.position
            to_move_up.position = pos_fin
            to_move_down.position = pos_start
            db.session.commit()
            return redirect( url_for('ToDo'))

@app.route("/todo/<int:id>/down", methods=['POST'])
def down(id):
    u_ID = request.cookies.get('userID')
    print(id)
    if request.method == 'POST':
        last_pos = ToDO.query.filter_by(username_id=u_ID).order_by(ToDO.position.desc()).first()
        to_move_down = ToDO.query.filter_by(username_id=u_ID, id=id).first()
        pos_start = to_move_down.position
        if int(id) == int(last_pos.id):
            return redirect( url_for('ToDo'))
        else:
            to_move_down = ToDO.query.filter_by(username_id=u_ID, id=id).first()
            pos_start = to_move_down.position
            to_move_up = ToDO.query.filter_by(username_id=u_ID, position=int(pos_start)+1).first()
            pos_fin = to_move_up.position
            to_move_up.position = pos_start
            to_move_down.position = pos_fin
            db.session.commit()
            return redirect( url_for('ToDo'))





if __name__ == "__main__":
    app.run(port=3000)
