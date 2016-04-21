import flask
import bcrypt
from init import app, db
import models


@app.route('/login')
def login():
    return flask.render_template('login.html')


@app.route('/login', methods=['POST'])
def handle_login():
    login = flask.request.form['user']
    password = flask.request.form['password']
    user = models.User.query.filter_by(login=login).first()
    if user is not None:
        pw_hash = bcrypt.hashpw(password.encode('utf8'), user.pw_hash)
        if pw_hash == user.pw_hash:
            flask.session['auth_user'] = user.id
            return flask.redirect(flask.request.form['url'], 303)
    return flask.render_template('login.html', state='bad')


@app.route('/create_user', methods=['POST'])
def create_user():
    login = flask.request.form['user']
    email = flask.request.form['email']
    password = flask.request.form['password']
    if password != flask.request.form['confirm']:
        return flask.render_template('login.html', state='password-mismatch')
    if len(login) > 20:
        return flask.render_template('login.html', state='bad-username')
    existing = models.User.query.filter_by(login=login).first()
    if existing is not None:
        return flask.render_template('login.html', state='username-used')
    if set(' [~!@#$%^&*()_+{}":;\']+$').intersection(login):
        return flask.render_template('login.html', state='bad-username')
    if not login:
        return flask.render_template('login.html', state='bad-username')
    if not password:
        return flask.render_template('login.html', state='bad-username')

    user = models.User()
    user.login = login
    user.email = email
    user.pw_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(15))
    db.session.add(user)
    db.session.commit()
    flask.session['auth_user'] = user.id
    return flask.redirect(flask.url_for('show_user', uid=user.id), 303)
