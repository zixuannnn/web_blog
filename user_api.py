import os

from flask import Flask, request, render_template, redirect, url_for, Blueprint, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth, Follow
from datetime import datetime

user_api = Blueprint('user_api', __name__)

@user_api.route('/search_user', methods = ['POST'])
def search_user():
    if 'id' in session:
        id = session['id']
    else:
        id = -1
    keyword = request.form['keyword']
    user_list = []
    post_list = []
    result_user, result_post = [], []
    if keyword != "":
        key = "%{}%".format(keyword)
        result_user = User.query.filter(User.username.like(key)).all()
        result_post = Posts.query.filter(Posts.title.like(key)).all()
    for i in result_user:
        user_list.append(i.__dict__)
    for i in result_post:
        post_list.append((i.__dict__))
    data = {"user":user_list,\
                "id": id, "post":post_list}
    return render_template('search_result_list.html', data=data)


@user_api.route('/following/<following_id>', methods=['GET','POST'])
def view_profile(following_id):
    if 'id' in session:
        id = session['id']
    else:
        id = -1
    following = User.query.filter(User.id == following_id).first()
    follower = User.query.filter(User.id == id).first()
    post_list = []
    post = Posts.query.filter(Posts.author_id==following_id).order_by(Posts.post_date.desc()).all()
    for p in post:
        post_list.append(p.__dict__)
    following_dict = following.__dict__
    if request.method == 'GET':
        data = {"following":following_dict,\
                "id": id, "filename":following_dict['photo'],\
                "post":post_list, "following_id":following_id}
        if id == following_id:
            return render_template('view_profile.html', data=data)
        return render_template('user_view_profile.html', data=data)
    else:
        if id == -1:
            return render_template("error_login_prompt.html")
        follow_record = Follow.query.filter(and_(Follow.follower_id==id, Follow.following_id==following_id)).first()
        if follow_record is not None:
            return render_template('Error.html', info="You have followed this user")
        if following_id == id:
            return render_template('Error.html', info="You cannot follow yourself")
        follow_input = Follow(follower_id=id, following_id=following_id)
        db.session.add(follow_input)
        db.session.commit()
        num_following = follower.following
        follower.following = num_following + 1
        num_follower = following.follower
        following.follower = num_follower + 1
        db.session.commit()
        return redirect(url_for('user_api.follow_user', following_id=following_id))


