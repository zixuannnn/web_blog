from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from web_config import app
from datetime import datetime
import json
import OAuth as oa


# init orm database
db = SQLAlchemy(app)

lm = LoginManager(app)
lm.login_view = 'index'

# Init tables using SQLAlchemy
# First table -> User
class User(db.Model):

    __tablename__ = "user"
    id = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(70), nullable=False)
    fName = db.Column(db.String(50))
    mName = db.Column(db.String(50))
    lName = db.Column(db.String(59))
    email = db.Column(db.String(70), nullable=False, unique=True)
    photo = db.Column(db.String(75))
    password_plain = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)
    registerDate = db.Column(db.DateTime, default=db.func.current_timestamp())
    lastLogin = db.Column(db.DateTime, default=db.func.current_timestamp())
    intro = db.Column(db.Text)
    profile = db.Column(db.Text)

    def __init__(self, username, id, fName, mName,lName, email, photo, password_plain, password_hash,
    	intro, profile, register_date, lastLogin):
        self.id = id
        self.username = username
        self.fName = fName
        self.mName = mName
        self.lName = lName
        self.email = email
        self.photo = photo
        self.password_plain = password_plain
        self.password_hash = password_hash
        self.intro = intro
        self.profile = profile
        self.registerDate = register_date
        self.lastLogin = lastLogin

# Second Table -> Posts
class Posts(db.Model):

	__tablename__ = "posts"
	post_id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
	author_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
	title = db.Column(db.String(100), nullable=False)
	post_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
	content = db.Column(db.Text)
	view_times = db.Column(db.Integer, default=0)
	thumbs_up = db.Column(db.BIGINT, default=0)

	def __init__(self, post_id, author_id, title, content, view_times, thumbs_up):
		self.post_id = post_id
		self.author_id = author_id
		self.title = title
		self.content = content
		self.view_times = view_times
		self.thumbs_up = thumbs_up

# Third Table -> PostComment
class Comment(db.Model):

    __tablename__ = "post_comments"
    comment_id = db.Column(db.BIGINT, autoincrement=True, primary_key=True)
    post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'))
    comment_author_id = db.Column(db.String(20), db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    comment_title = db.Column(db.String(100))
    thumbs_up = db.Column(db.Integer, default=0)

    def __init__(self, comment_id, post_id, comment_author_id, content, comment_title, thumbs_up):
        self.comment_id = comment_id
        self.post_id = post_id
        self.comment_author_id = comment_author_id
        self.content = content
        self.comment_title = comment_title
        self.thumbs_up = thumbs_up	

# Forth Table -> Category
class Category(db.Model):

    __tablename__ = "category"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(75), nullable=False)
    
    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name

# Fifth Table -> PostCategory
class PostCategory(db.Model):
    
    __tablename__ = "post_category"
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'), primary_key=True)

    def __init__(self, category_id, post_id):
        self.category_id = category_id
        self.post_id = post_id

# Sixth Table -> OAuth
class  OAuth(UserMixin, db.Model):

    __tablename__ = "oauth"
    social_id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(70), nullable=False)
    id = db.Column(db.String(20), db.ForeignKey('user.id'))
    register_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, social_id, email, id, register_date):
        self.social_id = social_id
        self.email = email
        self.id = id
        self.register_date = register_date






