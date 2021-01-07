import pytz
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth
from post_api import post_api
from user_api import user_api
from datetime import datetime
import json
import OAuth as oa
import random
import string
import os

lm = LoginManager(app)

app.register_blueprint(post_api)
app.register_blueprint(user_api)

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
	session.pop('id', None)
	session.pop('username', None)
	logout_user()
	return redirect(url_for('Main_Page'))

@app.route('/', methods=['GET'])
def Main_Page():
	if 'id' in session:
		id = session['id']
		return redirect(url_for('AfterLogin'))
	return render_template('main_page.html', login=False, id=-1)

@app.route('/main', methods=['GET'])
def AfterLogin():
	id = session['id']
	row = User.query.filter(User.id==id).first()
	session['id'] = row.id
	session['username'] = row.username
	return render_template('main_page.html', login=True, name=row.username, id=id)

@app.route('/login', methods=['GET', 'POST'])
def Login():
	if request.method == 'GET':
		if 'id' in session:
			id = session['id']
			row = User.query.filter(User.id == id).first()
			return render_template('last_login.html', id=id, date=row.lastLogin)
		return render_template('login.html')
	else:
		email = request.form['email']
		password = request.form['pwd']
		row = User.query.filter(User.email == email).first()
		last_login_date = row.lastLogin
		if row.password_plain == password:
			tz = pytz.timezone('Canada/Atlantic')
			date = datetime.now(tz=tz)
			row.lastLogin = date
			db.session.commit()
			session['id'] = row.id
			session['username'] = row.username
			login_user(row, True)
			return render_template('last_login.html', id=row.id, date=last_login_date)

@app.route('/authorize/<provider>')
def oauth_login(provider):
	tz = pytz.timezone('Canada/Atlantic')
	date = datetime.now(tz=tz)
	if not current_user.is_anonymous:
		row = User.query.filter(User.email==current_user.email).first()
		return redirect(url_for('AfterLogin'))
	oauth = oa.OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	tz = pytz.timezone('Canada/Atlantic')
	date = datetime.now(tz=tz)
	if not current_user.is_anonymous:
		email = current_user.email
		row = User.query.filter(current_user.email==email).first()
		return redirect(url_for('AfterLogin'))
	oauth = oa.OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None: # email is invalid
		return render_template('Error.html')
	user_record = OAuth.query.filter_by(social_id=social_id).first()
	if user_record is None:
		# generate a random id
		id = get_id(20)
		user = User(id=id, username=username, fName=None, mName=None,lName=None, email="", photo="default_photo.jpg", password_plain=social_id, \
					password_hash=str(hash(social_id)),intro = "No any introduction...", profile=None, register_date=date, lastLogin=date, \
					follower=0, following=0)
		db.session.add(user)
		db.session.commit()
		oauth_user = OAuth(social_id=social_id, email="", id=id, register_date=date)
		db.session.add(oauth_user)
		db.session.commit()
		user_record = User.query.filter_by(social_id=social_id).first()
	else:
		user_record = User.query.filter(User.id==user_record.id).first()
		user_record.lastLogin = date
		db.session.commit()
	login_user(user_record, True)
	session['id'] = user_record.id
	session['username'] = user_record.username
	return redirect(url_for('update_profile'))

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
			return render_template('Error.html', info="This email "+email+" has been used before, please choose another email...")
		password_hash = hash(password)
		id = get_id(20)
		tz = pytz.timezone('Canada/Atlantic')
		date = datetime.now(tz=tz)
		user = User(id=id, username=username, fName=None, mName=None,lName=None, email=email, photo="default_photo.jpg", password_plain=password, \
					password_hash=str(password_hash),intro = "No any introduction...", profile=None, register_date=date, lastLogin=date, follower=0, following=0)
		db.session.add(user)
		db.session.commit()
		user_record = User.query.filter_by(id=id).first()
		session['id'] = id
		session['username'] = username
		return redirect(url_for('update_profile'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
	if 'id' in session:
		row = User.query.filter(User.id==id).first()
		if request.method == 'GET':
			return render_template('update_profile.html', row=row)
		else:
			username = request.form['username']
			email = request.form['email']
			row.email = email
			row.username = username
			db.session.commit()
			return redirect(url_for('AfterLogin'))
	else:
		return render_template('error_login_prompt.html')

@app.route('/profile_page', methods=['GET', 'POST'])
def profile():
	id = session['id']
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
				return render_template('Error.html', info="check the type of the uploaded file")
			base_path = os.path.abspath(os.path.dirname(__file__))
			filename = row.id + "." + file.filename.split(".")[1];
			up_path = os.path.join(base_path, "static", filename)
			# if os.path.exists(up_path):
			# 	os.remove(up_path)
			file.save(up_path)
			row.photo = filename
			db.session.commit()
		if username != "":
			row.username = username
		if email != "":
			row.email = email
		if lName != "":
			row.lName = lName
		if mName != "":
			row.mName = mName
		if fName != "":
			row.fName = fName
		if intro != "":
			row.intro = intro
		db.session.commit()
		return redirect(url_for('profile'))

@app.route('/category_python', methods=['GET'])
def category_python():
	python_list = Posts.query.join(PostCategory, PostCategory.post_id == Posts.post_id). \
		filter(PostCategory.category_id == 1).order_by(Posts.post_date.desc()).all()
	new_python_list = []
	for p in python_list:
		new_python_list.append(p.__dict__)
	data = {"list":new_python_list}
	if 'id' not in session:
		data["id"] = -1
		return render_template('category_python.html', data=data)
	else:
		id = session['id']
		user = User.query.filter(User.id == id).first()
		data["id"] = id
		data["name"] = user.username
		return render_template('category_python.html', data=data)

@app.route('/category_java', methods=['GET'])
def category_java():
	java_list = Posts.query.join(PostCategory, PostCategory.post_id == Posts.post_id). \
		filter(PostCategory.category_id == 2).order_by(Posts.post_date.desc()).all()
	new_java_list = []
	for p in java_list:
		new_java_list.append(p.__dict__)
	data = {"list":new_java_list}
	if 'id' not in session:
		data["id"] = -1
		return render_template('category_java.html', data=data)
	else:
		id = session['id']
		user = User.query.filter(User.id == id).first()
		data["id"] = id
		data["name"] = user.username
		return render_template('category_java.html', data=data)

@app.route('/category_mysql', methods=['GET'])
def category_mysql():
	mysql_list = Posts.query.join(PostCategory, PostCategory.post_id == Posts.post_id). \
		filter(PostCategory.category_id == 3).order_by(Posts.post_date.desc()).all()
	new_mysql_list = []
	for p in mysql_list:
		new_mysql_list.append(p.__dict__)
	data = {"list": new_mysql_list}
	if 'id' not in session:
		data["id"] = -1
		return render_template('category_mysql.html', data=data)
	else:
		id = session['id']
		user = User.query.filter(User.id == id).first()
		data["id"] = id
		data["name"] = user.username
		return render_template('category_mysql.html', data=data)



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)




