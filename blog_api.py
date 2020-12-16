from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth
from datetime import datetime
import json
import OAuth as oa
import random
import string

lm = LoginManager(app)
#lm.login_view = 'index'

def get_id(length):
    # Used to get a random user id
    letters = string.ascii_letters+string.digits
    random_id = ''.join(random.choice(letters) for i in range(length))
    return random_id

@lm.user_loader
def load_user(id):
    return OAuth.query.get(id)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Main_Page'))

@app.route('/', methods=['GET'])
def Main_Page():
	return render_template('main_page.html', login=False)

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
		if row.password_plain == password:
			return redirect(url_for('AfterLogin', id=row.id))

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

@app.route('/category_python/<id>', methods=['GET'])
def category_python(id):
	data = Posts.query.order_by(Posts.post_id.desc()).limit(4).all()
	return render_template('category_python.html', id=id, row1=data[0], row2=data[1], row3=data[2], row4=data[3])

@app.route('/post1/<id>')
def recent_posts(id, post_id):
	post = Posts.query.filter(Posts.post_id==post_id).first()
	return # render_template


# @app.route('/signup', methods=['GET', 'POST'])
# def signUp():
#     if request.method == 'GET':
#         return render_template('...')
#     else:
#         pass

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)




