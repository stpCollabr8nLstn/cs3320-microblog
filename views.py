import base64
import flask
import models
import os
import jinja2
from sqlalchemy.orm import joinedload
from init import app, db
from sqlalchemy import or_
from sqlalchemy import desc


@app.before_request
def setup_csrf():
    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = base64.b64encode(os.urandom(32)).decode('ascii')


@app.before_request
def setup_user():
    if 'auth_user' in flask.session:
        user = models.User.query.get(flask.session['auth_user'])
        if user is None:
            del flask.session['auth_user']
        flask.g.user = user


@app.route('/')
def index():
    recent_posts = models.Posts.query.order_by(desc(models.Posts.timestamp)).limit(20).all()
    return flask.render_template('index.html', csrf_token=flask.session['csrf_token'], recent_posts=recent_posts)


@app.route('/user/<int:uid>')
def show_user(uid):
    user = models.User.query.get_or_404(uid)
    user_posts = models.Posts.query.filter_by(creator_id=user.id).order_by(desc(models.Posts.timestamp)).limit(10).all()
    for post in user_posts:
        pass
    return flask.render_template('user.html', user=user, user_posts=user_posts)


@app.route('/logout')
def logout():
    del flask.session['auth_user']
    return flask.redirect(flask.url_for('login'))


@app.route('/edit_user/<int:uid>')
def edit_user(uid):
    user = models.User.query.get_or_404(uid)
    return flask.render_template('edit_user.html', user=user)

@app.route('/all_users')
def all_users():
    user_list = models.User.query.order_by(models.User.login)
    return flask.render_template('all_users.html', user_list = user_list)


@app.errorhandler(404)
def not_found(err):
    return flask.render_template('404.html', path=flask.request.path), 404