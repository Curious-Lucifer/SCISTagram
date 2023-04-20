from flask import Flask, session, redirect, render_template, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha512
import os


# init
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + os.environ['MYSQL_USER'] + ':' + os.environ['MYSQL_PASSWORD'] + '@mysql:3306/' + os.environ['MYSQL_DATABASE']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.LargeBinary(64), nullable=False)
    passwd_hash = db.Column(db.LargeBinary(64), nullable=False)

class Post_Data(db.Model):
    __tablename__ = 'post_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_user = db.Column(db.LargeBinary(64), nullable=False)
    post_msg = db.Column(db.LargeBinary(4096), nullable=False)
    accept_xss = db.Column(db.Boolean, nullable=False, default=True)
    accept_ssti = db.Column(db.Boolean, nullable=False, default=False)

ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']


# user control
def verify(username: str, password: str):
    if (username == 'admin') and (password == ADMIN_PASSWORD):
        return True
    if User.query.filter_by(username=username.encode(), passwd_hash=sha512(password.encode()).digest()).count() == 1:
        return True
    return False

def create_user(username: str, password: str):
    if (username == 'admin') or (User.query.filter_by(username=username.encode()).count() != 0):
        return False, "* User already exist"
    if len(username.encode()) > 64:
        return False, "* Username is too long"

    new_user = User(username=username.encode(), passwd_hash=sha512(password.encode()).digest())
    db.session.add(new_user)
    db.session.commit()

    return True, ""


# general view
@app.route('/')
def index():
    if not 'username' in session:
        return redirect('/login')
    
    post_data_list = []
    for post_data in reversed(Post_Data.query.all()):
        if post_data.accept_ssti:
            post_data_list.append({'post_user': post_data.post_user.decode(), 'post_msg': render_template_string(post_data.post_msg.decode()), 'accept_xss': post_data.accept_xss})
        else:
            post_data_list.append({'post_user': post_data.post_user.decode(), 'post_msg': post_data.post_msg.decode(), 'accept_xss': post_data.accept_xss})

    return render_template('index.html', post_data_list=post_data_list, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html')

    if not (('username' in request.form) and ('password' in request.form)):
        return render_template('404.html'), 200

    if (request.form['username'] == '') or (request.form['password'] == ''):
        return render_template('login.html', error_msg="* Username/Password can't be blank")

    if verify(request.form['username'], request.form['password']):
        session['username'] = request.form['username']
        return redirect('/')
    else:
        return render_template('login.html', error_msg='* Incorrect Username/Password')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/')

    if request.method == 'GET':
        return render_template('signup.html')

    if not (('username' in request.form) and ('password' in request.form)):
        return render_template('404.html'), 200

    if (request.form['username'] == '') or (request.form['password'] == ''):
        return render_template('signup.html', error_msg="* Username/Password can't be blank")

    correct, error_msg = create_user(request.form['username'], request.form['password'])
    if correct:
        session['username'] = request.form['username']
        return redirect('/')
    else:
        return render_template('signup.html', error_msg=error_msg)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 200

@app.post('/post')
def post():
    if not 'username' in session:
        return redirect('/login')

    if not 'msg' in request.form:
        return render_template('404.html'), 200

    if (request.form['msg'] != '') and (len(request.form['msg'].encode()) < 4096):
        new_post_data = Post_Data(post_user=session['username'].encode(), post_msg=request.form['msg'].encode())
        db.session.add(new_post_data)
        db.session.commit()

    return redirect('/')


# admin view
@app.route('/admin')
def admin_view():
    if (not 'username' in session) or (session['username'] != 'admin'):
        return render_template('404.html'), 200

    user_list = User.query.all()

    post_data_list = Post_Data.query.all()
    post_data_list.reverse()

    return render_template('admin.html', user_list=user_list, post_data_list=post_data_list)

@app.post('/admin/user_update')
def user_update():
    if (not 'username' in session) or (session['username'] != 'admin'):
        return render_template('404.html'), 200
    
    if (request.form['username'] == '') or (len(request.form['username'].encode()) > 64):
        return redirect('/admin')
    
    if (request.form['username'] == 'admin') or (User.query.filter_by(username=request.form['username'].encode()).count() == 1):
        return redirect('/admin')

    user = User.query.filter_by(id=int(request.form['id'])).first()

    user_posts = Post_Data.query.filter_by(post_user=user.username).all()
    for user_post in user_posts:
        user_post.post_user = request.form['username'].encode()

    user.username = request.form['username'].encode()
    if request.form['password'] != '':
        user.passwd_hash = sha512(request.form['password'].encode()).digest()
    db.session.commit()

    return redirect('/admin')

@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    if (not 'username' in session) or (session['username'] != 'admin'):
        return render_template('404.html'), 200
    
    user = User.query.filter_by(id=id).first()

    user_posts = Post_Data.query.filter_by(post_user=user.username).all()
    for user_post in user_posts:
        db.session.delete(user_post)
    
    db.session.delete(user)
    db.session.commit()

    return redirect('/admin')

@app.post('/admin/post_update')
def post_update():
    if (not 'username' in session) or (session['username'] != 'admin'):
        return render_template('404.html'), 200
    
    if (request.form['msg'] == '') or (len(request.form['msg'].encode()) >= 4096):
        return redirect('/admin')

    post_data = Post_Data.query.filter_by(id=int(request.form['id'])).first()
    post_data.post_msg = request.form['msg'].encode()
    print('Hello')
    print(request.form)
    if 'accept_xss' in request.form:
        post_data.accept_xss = True
    else:
        post_data.accept_xss = False
    if 'accept_ssti' in request.form:
        post_data.accept_ssti = True
    else:
        post_data.accept_ssti = False
    db.session.commit()

    return redirect('/admin')

@app.route('/admin/delete_post/<int:id>')
def delete_post(id):
    if (not 'username' in session) or (session['username'] != 'admin'):
        return render_template('404.html'), 200
    
    post_data = Post_Data.query.filter_by(id=id).first()
    db.session.delete(post_data)
    db.session.commit()

    return redirect('/admin')