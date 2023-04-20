from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, time, sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + os.environ['MYSQL_USER'] + ':' + os.environ['MYSQL_PASSWORD'] + '@mysql:3306/' + os.environ['MYSQL_DATABASE']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)

with app.test_request_context():
    print('Waiting for MySQL Database to be ready', end='', flush=True)
    while True:
        try:
            db.engine.raw_connection()
            print()
            break
        except:
            print('.', end='', flush=True)
            time.sleep(1)
    print('MySQL Database is ready')

    if ('INIT' in os.environ) and (os.environ['INIT'] == 'true'):
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

        db.drop_all()
        db.create_all()

        print('Database Successfully Initialized')

    sys.exit()