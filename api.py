import flask
import flask_socketio as sio
import re
import urllib
from init import app, db, socketio
import models
import io


def post_message(creator, content, file):
    post = models.Posts()
    post.content = content
    post.creator_id = creator
    if file is not None:
        post.photo_type = file.mimetype
        # get the photo content. we read it into a 'BytesIO'
        photo_data = io.BytesIO()
        file.save(photo_data)
        post.photo = photo_data.getvalue()

    db.session.add(post)
    db.session.commit()
    return post


@socketio.on('connect')
def on_connect():
    uid = flask.session.get('auth_user', None)
    if uid is None:
        app.logger.warn('received socket connection from unauthed user')
        return
    app.logger.info('new client connected for user %d', uid)
    sio.join_room('user-{}'.format(uid))


@socketio.on('disconnect')
def on_disconnect():
    app.logger.info('client disconnected')


def check_request():
    token = flask.session['csrf_token']
    if flask.request.form['_csrf_token'] != token:
        app.logger.warn('invalid CSRF token')
        flask.abort(400)
    if flask.session.get('auth_user') != int(flask.request.form['init_id']):
        app.logger.warn('requesting user %s not logged in (%s)',
                        flask.request.form['init_id'],
                        flask.session.get('auth_user'))
        flask.abort(403)


@app.route('/follow/request', methods=['POST'])
def request_follow():
    check_request()
    init = int(flask.request.form['init_id'])
    print(init)
    other = int(flask.request.form['respond_id'])
    print(other)
    fs = models.Follow.query.filter_by(init_id=init, respond_id=other).first()
    if fs is None:
        fs = models.Follow()
        fs.init_id = init
        fs.respond_id = other
        db.session.add(fs)
        db.session.commit()

    # Following now!
    return flask.jsonify({'new_state': 'following'})


@app.route('/follow/destroy', methods=['POST'])
def destroy_follow():
    check_request()
    init = flask.request.form['init_id']
    other = flask.request.form['respond_id']
    fs = models.Follow.query.filter_by(init_id=init, respond_id=other).first()
    if fs is not None:
        db.session.delete(fs)
        db.session.commit()
        return flask.jsonify({'new_state': 'none'})


@app.route('/follow/retract', methods=['POST'])
def retract_follow():
    # this is the same as destroy
    return destroy_follow()


@app.route('/user/post', methods=['POST'])
def handle_post():
    check_request()
    creator = flask.request.form['init_id']
    content = flask.request.form['content']
    file = flask.request.files['image']
    print('5')
    # verify correct file type
    if not file.mimetype.startswith('image/'):
        file = None
    post_message(creator, content, file)
    return flask.redirect(flask.url_for('show_user', uid=creator), code=303)


@app.route('/post/<int:post_id>/photo')
def show_photo(post_id):
    post = models.Posts.query.get_or_404(post_id)
    return flask.send_file(io.BytesIO(post.photo))


@app.route('/edit_user/post', methods=['POST'])
def handle_update():
    check_request()
    locale = flask.request.form['location']
    bio = flask.request.form['short_bio']
    uid = flask.request.form['init_id']
    email = flask.request.form['email']
    user = models.User.query.get_or_404(uid)
    if email is None:
        email = models.User.query.get(user.email)
    print(user.email)
    print(email)
    user.location = locale
    user.short_bio = bio
    user.email = email
    db.session.add(user)
    db.session.commit()
    return flask.redirect(flask.url_for('show_user', uid=uid), code=303)

