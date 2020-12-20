from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth
from post_api import post_api
from datetime import datetime
import json
import OAuth as oa
import random
import string
import os

lm = LoginManager(app)
#lm.login_view = 'index'

app.register_blueprint(post_api)

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def get_id(length):
    # Used to get a random user id
    letters = string.ascii_letters+string.digits
    random_id = ''.join(random.choice(letters) for i in range(length))
    return random_id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@lm.user_loader
def load_user(id):
    return OAuth.query.get(id)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Main_Page'))

@app.route('/', methods=['GET'])
def Main_Page():
	return render_template('main_page.html', login=False, id=-1)

@app.route('/main/<id>', methods=['GET'])
def AfterLogin(id):
	row = User.query.filter(User.id==id).first()
	return render_template('main_page.html', login=True, name=row.username, id=id)

@app.route('/login', methods=['GET', 'POST'])
def Login():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		email = request.form['email']
		password = request.form['pwd']
		row = User.query.filter(User.email==email).first()
		last_login_date = row.lastLogin
		if row.password_plain == password:
			date = datetime.now()
			row.lastLogin = date
			db.session.commit()
			return render_template('last_login.html', id=row.id, date=last_login_date)

@app.route('/authorize/<provider>')
def oauth_login(provider):
	date = datetime.now()
	if not current_user.is_anonymous:
		row = User.query.filter(User.email==current_user.email).first()
		return redirect(url_for('AfterLogin', id=row.id))
	oauth = oa.OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	date = datetime.now()
	if not current_user.is_anonymous:
		email = current_user.email
		row = User.query.filter(current_user.email==email).first()
		return redirect(url_for('AfterLogin', id=row.id))
	oauth = oa.OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None: # email is invalid
		return render_template('Error.html')
	user_record = OAuth.query.filter_by(social_id=social_id).first()
	if user_record is None:
		# generate a random id
		id = get_id(20)
		user = User(id=id, username=username, fName=None, mName=None,lName=None, email="", photo=None, password_plain=social_id, password_hash=str(hash(social_id)),intro = None, profile=None, register_date=date, lastLogin=date)
		db.session.add(user)
		db.session.commit()
		oauth_user = OAuth(social_id=social_id, email="", id=id, register_date=date)
		db.session.add(oauth_user)
		db.session.commit()
		user_record = OAuth.query.filter_by(social_id=social_id).first()
	else:
		row = User.query.filter(User.id==user_record.id).first()
		row.lastLogin = date
		db.session.commit()
	login_user(user_record, True)
	user_record = OAuth.query.filter_by(social_id=social_id).first()
	return redirect(url_for('update_profile', id=user_record.id))

@app.route('/signup', methods=['GET', 'POST'])
def SignUp():
	if request.method == 'GET':
		return render_template('signup.html')
	else:
		username = request.form['un']
		password = request.form['pwd']
		email = request.form['email']
		email_eligible = User.query.filter(User.email==email).first()
		if email_eligible is not None:
			return render_template('Error.html')
		password_hash = hash(password)
		id = get_id(20)
		date = datetime.now()
		user = User(id=id, username=username, fName=None, mName=None,lName=None, email=email, photo="default_photo.jpg", password_plain=password, password_hash=str(password_hash),intro = None, profile=None, register_date=date, lastLogin=date)
		db.session.add(user)
		db.session.commit()
		user_record = User.query.filter_by(id=id).first()
		login_user(user_record, True)
		return redirect(url_for('update_profile', id=id))

@app.route('/update_profile/<id>', methods=['GET', 'POST'])
def update_profile(id):
	row = User.query.filter(User.id==id).first()
	if request.method == 'GET':
		return render_template('update_profile.html', row=row, id=id)
	else:
		username = request.form['username']
		email = request.form['email']
		row.email = email
		row.username = username
		db.session.commit()
		return redirect(url_for('AfterLogin', id=id))

@app.route('/profile_page/<id>', methods=['GET', 'POST'])
def profile(id):
	row = User.query.filter(User.id == id).first()
	if request.method == 'GET':
		if row:
			return render_template('profile.html', id=id, filename=row.photo, row=row)
		else:
			return render_template('error_login_prompt.html')
	else:
		username = request.form['username']
		email = request.form['email']
		lName = request.form['lName']
		mName = request.form['mName']
		fName = request.form['fName']
		intro = request.form['intro']

		file = request.files.get("files")
		if file:
			if not allowed_file(file.filename):
				print("check the type of the uploaded file")
				return render_template('Error.html')
			base_path = os.path.abspath(os.path.dirname(__file__))
			filename = row.id + "." +file.filename.split(".")[1];
			up_path = os.path.join(base_path, "static", filename)
			file.save(up_path)
			row.photo = filename
			db.session.commit()

		row.username = username
		row.email = email
		row.lName = lName
		row.mName = mName
		row.fName = fName
		row.intro = intro
		db.session.commit()
		return redirect(url_for('profile', id=id))

@app.route('/category_python/<id>', methods=['GET'])
def category_python(id):
	if id == "-1":
		id = -1
	else:
		user = User.query.filter(User.id == id).first()
	python_list = Posts.query.join(PostCategory, PostCategory.post_id==Posts.post_id). \
		add_columns(Posts.post_id, Posts.view_times, Posts.post_date, Posts.author_id, Posts.content, Posts.title, Posts.thumbs_up). \
		filter(PostCategory.category_id==1).order_by(Posts.post_date.desc()).limit(4).all()
	new_python_list = [-1, -1, -1, -1]
	for c in range(len(python_list)):
		new_python_list[c] = python_list[c]
	return render_template('category_python.html', id=id, name=user.username, row1=new_python_list[0], row2=new_python_list[1], row3=new_python_list[2], row4=new_python_list[3])

@app.route('/category_java/<id>', methods=['GET'])
def category_java(id):
	if id == "-1":
		id = -1
	else:
		user = User.query.filter(User.id == id).first()
	java_list = Posts.query.join(PostCategory, PostCategory.post_id==Posts.post_id). \
		add_columns(Posts.post_id, Posts.view_times, Posts.post_date, Posts.author_id, Posts.content, Posts.title, Posts.thumbs_up). \
		filter(PostCategory.category_id==2).order_by(Posts.post_date.desc()).limit(4).all()
	new_java_list = [-1, -1, -1, -1]
	for c in range(len(java_list)):
		new_java_list[c] = java_list[c]
	return render_template('category_java.html', id=id, name=user.username, row1=new_java_list[0], row2=new_java_list[1], row3=new_java_list[2], row4=new_java_list[3])

@app.route('/category_mysql/<id>', methods=['GET'])
def category_mysql(id):
	if id == "-1":
		id = -1
	else:
		user = User.query.filter(User.id == id).first()
	mysql_list = Posts.query.join(PostCategory, PostCategory.post_id==Posts.post_id). \
		add_columns(Posts.post_id, Posts.view_times, Posts.post_date, Posts.author_id, Posts.content, Posts.title, Posts.thumbs_up). \
		filter(PostCategory.category_id==3).order_by(Posts.post_date.desc()).limit(4).all()
	new_mysql_list = [-1, -1, -1, -1]
	for c in range(len(mysql_list)):
		new_mysql_list[c] = mysql_list[c]
	return render_template('category_mysql.html', id=id, name=user.username, row1=new_mysql_list[0], row2=new_mysql_list[1], row3=new_mysql_list[2], row4=new_mysql_list[3])



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)




