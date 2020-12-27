from flask import Flask, request, render_template, redirect, url_for, Blueprint
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
    view_time = post.view_times
    post.view_times = view_time + 1
    db.session.commit()
    author_id = post.author_id
    author = User.query.filter(User.id == author_id).first()
    comment_list = Comment.query.join(User, User.id==Comment.comment_author_id).\
        filter(Comment.post_id==post_id).order_by(Comment.published_date.desc()).all()
    new_comment_list = []
    for c in comment_list:
        new_comment_list.append(c.__dict__)
    post_dict = post.__dict__
    author = author.__dict__

    if request.method == 'GET':
        if id != "-1":
            user = User.query.filter(User.id == id).first()
            data = {"comment":new_comment_list, "id":id, "name":user.username, "post":post_dict,\
                    "login":1, "author":author}
            if user:
                return render_template('post.html', data=data)
        else:
            data = {"comment": new_comment_list, "id": -1, "post": post_dict, \
                    "login": -1, "author": author}
            return render_template('post.html', data=data)
    else:
        if id != "-1":
            comment = request.form['comment']
            title = request.form['comment_title']
            if comment == "" or title == "":
                return render_template('Error.html', info="Please fill out your title or comment content")
            date = datetime.now()
            comment_input = Comment(post_id=post_id, comment_author_id=id, \
                                    content=comment, comment_title=title, thumbs_up=0, published_date=date)
            db.session.add(comment_input)
            db.session.commit()
            return redirect(url_for('post_api.recent_posts', id=id, post_id=post_id))
        else:
            return render_template('error_login_prompt.html')

@post_api.route('/share_new_post/<id>', methods=['GET', 'POST'])
def new_post(id):
    if request.method == 'GET':
        if id == "-1":
            return render_template('new_post.html', login=-1, id=-1)
        else:
            user = User.query.filter(User.id == id).first()
            return render_template('new_post.html', login=1, id=id, name=user.username)
    else:
        if id != "-1":
            article = request.form['article']
            title = request.form['article_title']
            date = datetime.now()
            post_input = Posts(author_id=id, title=title, content=article, view_times=0, thumbs_up=0, post_date=date)
            db.session.add(post_input)
            db.session.commit()
            post_id = db.session.query(func.max(Posts.post_id)).scalar()
            print(post_id)
            if request.form.get('python'):
                category = PostCategory(post_id=post_id, category_id=1)
                db.session.add(category)
                db.session.commit()
            if request.form.get('java'):
                category = PostCategory(post_id=post_id, category_id=2)
                db.session.add(category)
                db.session.commit()
            if request.form.get('mysql'):
                category = PostCategory(post_id=post_id, category_id=3)
                db.session.add(category)
                db.session.commit()
            return redirect(url_for('AfterLogin', id=id))
        else:
            return render_template('error_login_prompt.html')

@post_api.route('/comment_like/<id>/<comment_id>/<post_id>')
def comment_like(id, comment_id, post_id):
    comment = Comment.query.filter(Comment.comment_id == comment_id).first()
    comment_likes = comment.thumbs_up
    comment.thumbs_up = comment_likes + 1
    db.session.commit()
    post = Posts.query.filter(Posts.post_id == post_id).first()
    view_time = post.view_times
    post.view_times = view_time - 1
    db.session.commit()
    return redirect(url_for('post_api.recent_posts', id=id, post_id=post_id))





