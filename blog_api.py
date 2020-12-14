from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth
import json
import OAuth as oa
import random
import string

lm = LoginManager(app)
lm.login_view = 'index'

def get_id(length):
    # Used to get a random user id
    letters = string.ascii_letters+string.digits
    random = ''.join(random.choice(letters) for i in range(length))
    return result_str

@app.route('/authorize/<provider>')
def oauth_login(provider):
    if not current_user.is_anonymous:
        return # redirect to oauth login
    oauth = oa.OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        email = current_user.email
        social_id = current_user.social_id
        id = OAuth.query.filter(oauth.email==email).first().id
        return # redirect to oauth login
    oauth = oa.OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None: # email is invalid
        flash('OAuth Failed')
        return render_template('Error.html')
    user = OAuth.query.filter(oauth.social_id==social_id).first()
    if user is None:
        # generate a random id
        id = get_id(20)
        oauth_user = OAuth(social_id=social_id, email=email, id=id)
        db.session.add(oauth_user)
        db.session.commit()
        user = User(id=id, fName=None, mName=None,lName=None, email=email, photo=None, password_plain=social_id, password_hash=str(hash(social_id)),
        intro = None, profile=None)
        db.session.add(user)
        db.session.commit()
    user = OAuth.query.filter(oauth.social_id==social_id).first()
    login_user(user, True)
    return redirect(url_for('...'))

@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        return render_template('...')
    else:
        pass




