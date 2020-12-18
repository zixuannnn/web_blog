from flask import Flask, request, render_template, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from sqlalchemy import func

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
    comment_list = Comment.query.join(User, User.id==Comment.comment_author_id).\
        add_columns(User.username, Comment.content, Comment.thumbs_up, Comment.published_date, Comment.comment_title).\
        filter(Comment.post_id==post_id).order_by(Comment.published_date.desc()).limit(4).all()
    new_comment_list = [None, None, None, None]
    for c in range(len(comment_list)):
        new_comment_list[c] = comment_list[c]

    if request.method == 'GET':
        if id != "-1":
            user = User.query.filter(User.id == id).first()
            if user:
                return render_template('post.html', id=id, name=user.username, post=post, author=author, comment1=new_comment_list[0], comment2=new_comment_list[1],\
                                       comment3=new_comment_list[2],comment4=new_comment_list[3], login=1)
        else:
            return render_template('post.html', id=id, post=post, author=author, comment1=new_comment_list[0], comment2=new_comment_list[1],\
                                       comment3=new_comment_list[2],comment4=new_comment_list[3], login=-1)
    else:
        if id != "-1":
            comment = request.form['comment']
            title = request.form['comment_title']
            date = datetime.now()
            comment_input = Comment(post_id=post_id, comment_author_id=id, content=comment, comment_title=title, thumbs_up=0, published_date=date)
            db.session.add(comment_input)
            db.session.commit()
            return redirect(url_for('post_api.recent_posts', id=id, post_id=post_id))
        else:
            return render_template('error_login_prompt.html')

@post_api.route('/share_new_post/<id>', methods=['GET', 'POST'])
def new_post(id):
    if request.method == 'GET':
        if id == "-1":
            return render_template('new_post.html', login=-1)
        else:
            return render_template('new_post.html', login=1)
    else:
        if id != "-1":
            article = request.form['article']
            title = request.form['article_title']
            # date = datetime.now()
            # post_input = Posts(author_id=id, title=title, content=article, view_times=0, thumbs_up=0)
            # db.session.add(post_input)
            # db.session.commit()
            post_id = Posts.query(func.max(User.numLogins)).scalar()
            if request.form.get('python'):
                print(1)
                # category = PostCategory(post_id=post_id, category_id=1)
                # db.session.add(post_input)
                # db.session.commit()
            if request.form.get('java'):
                print(2)
                # category = PostCategory(post_id=post_id, category_id=2)
                # db.session.add(post_input)
                # db.session.commit()
            if request.form.get('category3'):
                print(3)
                # category = PostCategory(post_id=post_id, category_id=3)
                # db.session.add(post_input)
                # db.session.commit()
            return redirect(url_for('Main_Page'))
        else:
            return render_template('error_login_prompt.html')





