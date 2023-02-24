from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
import pymysql
pymysql.install_as_MySQLdb()

with open('config.json', 'r') as c:
  params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.config.update(
  MAIL_SERVER = 'smtp.gmail.com',
  MAIL_PORT = '465',
  MAIL_USE_SSL = True,
  MAIL_USERNAME = params['gmail-user'],
  MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)
if(local_server):
  app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
  sno = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  phone_num = db.Column(db.String(12), nullable=False)
  msg = db.Column(db.String(120), nullable=False)
  date = db.Column(db.String(12), nullable=True)
  email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
  sno = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  slug = db.Column(db.String(21), nullable=False)
  content = db.Column(db.String(120), nullable=False)
  tagline = db.Column(db.String(120), nullable=False)
  date = db.Column(db.String(12), nullable=True)
  img_file = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
  posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
  return render_template('index.html', params=params, posts=posts)

@app.route("/post/<string:post_slug>", methods=["GET"])
def post_route(post_slug):
  post = Posts.query.filter_by(slug=post_slug).first()
  return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
  return render_template('about.html', params=params)

@app.route("/dashboard")
def dashboard():
  return render_template('login.html', params=params)

@app.route("/contact", methods=["GET", "POST"])
def contact():
  if(request.method == 'POST'):
    '''Add entru to database'''
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date= datetime.now())
    db.session.add(entry)
    db.session.commit()
    mail.send_message('New message from Blog', sender=email, recipients = [params['gmail-user']],body = message + "\n" + phone)
  return render_template('contact.html', params=params)

@app.route("/post")
def post():
  return render_template('post.html', params=params)

app.run(debug=True)