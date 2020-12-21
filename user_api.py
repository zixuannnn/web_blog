from flask import Flask, request, render_template, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from sqlalchemy import func
from web_config import app
from blog_table import db, User, Posts, Comment, Category, PostCategory, OAuth
from datetime import datetime
import OAuth as oa
import random
import string

user_api = Blueprint('user_api', __name__)

@user_api.route('/search_user/<id>', methods = ['POST'])
def search_user(id):
    keyword = request.form['keyword']
    user_list = [-1, -1, -1, -1]
    result = []
    if keyword != "":
        key = "%{}%".format(keyword)
        result = User.query.filter(User.username.like(key)).all()
    for i in range(len(result)):
        user_list[i] = result[i]
    return render_template('search_result_list.html', id=id, row1=user_list[0], row2=user_list[1], row3=user_list[2], row4=user_list[3])
