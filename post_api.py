from flask import Flask, request, render_template, redirect, url_for, Blueprint
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

post_api = Blueprint('post_api', __name__)

@post_api.route('/post/<id>/<post_id>', methods=['GET', 'POST'])
def recent_posts(id, post_id):
    post = Posts.query.filter(Posts.post_id == post_id).first()
    author_id = post.author_id
    author = User.query.filter(User.id == author_id).first()
    comment_list = Comment.query.filter(Comment.post_id==post_id).order_by(Comment.published_date.desc()).limit(4).all
    print(comment_list)
    #data = Posts.query.order_by(Posts.post_id.desc()).limit(4).all()

    if request.method == 'GET':
        if id != "-1":
            user = User.query.filter(User.id == id).first()
            if user:
                return render_template('post.html', id=id, name=user.username, post=post, user=author)
        else:
            return render_template('post.html', id=id, post=post, author=author)
    else:
        if id != "-1":
            comment = request.form['comment']
            title = request.form['comment_title']
            date = datetime.now()
            comment_input = Comment(post_id=post_id, comment_author_id=id, content=comment, comment_title=title, thumbs_up=0, published_date=date)
            db.session.add(comment_input)
            db.session.commit()
            user = User.query.filter(User.id == id).first()
            return render_template('post.html', id=id, name=user.username, post=post, user=author)
        else:
            return render_template('error_login_prompt.html')




