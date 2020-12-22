import os

from flask import Flask, request, render_template, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth, Follow
from datetime import datetime

user_api = Blueprint('user_api', __name__)

@user_api.route('/search_user/<id>', methods = ['POST'])
def search_user(id):
    keyword = request.form['keyword']
    user_list = [-1, -1, -1, -1]
    post_list = [-1, -1, -1, -1]
    result_user, result_post = [], []
    if keyword != "":
        key = "%{}%".format(keyword)
        result_user = User.query.filter(User.username.like(key)).all()
        result_post = Posts.query.filter(Posts.title.like(key)).all()
    for i in range(len(result_user)):
        user_list[i] = result_user[i]
    for i in range(len(result_post)):
        post_list[i] = result_post[i]
    return render_template('search_result_list.html', id=id, row1=user_list[0], row2=user_list[1], row3=user_list[2], row4=user_list[3],\
                           post1=post_list[0], post2=post_list[1], post3=post_list[2], post4=post_list[3])

@user_api.route('/following/<id>/<following_id>', methods=['GET','POST'])
def follow_user(id, following_id):
    following = User.query.filter(User.id == following_id).first()
    follower = User.query.filter(User.id == id).first()
    post_list = [-1,-1,-1,-1]
    post = Posts.query.filter(Posts.author_id==following_id).order_by(Posts.post_date.desc()).limit(4).all()
    # base_path = os.path.abspath(os.path.dirname(__file__))
    # path = os.path.join(base_path, "static", following.photo)
    for i in range(len(post)):
        post_list[i] = post[i]
    if request.method == 'GET':
        return render_template('user_view_profile.html', following=following, id=id,filename=following.photo, \
                               row1=post_list[0], row2=post_list[1], row3=post_list[2], row4=post_list[3])
    else:
        if id == "-1":
            return render_template('error_login_prompt.html')
        follow_record = Follow.query.filter(Follow.follower_id==id and Follow.following_id==following_id).first()
        if follow_record is not None:
            return render_template('Error.html', info="You have followed this user")
        follow_input = Follow(follower_id=id, following_id=following_id)
        db.session.add(follow_input)
        db.session.commit()
        num_following = follower.following
        follower.following = num_following + 1
        num_follower = following.follower
        following.follower = num_follower + 1
        db.session.commit()
        return redirect(url_for('user_api.follow_user', id=id, following_id=following_id))


