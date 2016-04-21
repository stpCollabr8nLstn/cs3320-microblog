import hashlib
import datetime
from init import app, db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    pw_hash = db.Column(db.String(64))
    location = db.Column(db.String(40))
    short_bio = db.Column(db.String(200))

    def follow_state(self, other):
        if self.id == other:
            return 'self'
        forward = Follow.query.filter_by(init_id=self.id, respond_id=other).first()
        if forward:
            return 'following'
        else:
            return 'none'

    @property
    def grav_hash(self):
        hash = hashlib.md5()
        hash.update(self.email.strip().lower().encode('utf8'))
        return hash.hexdigest()

    @property
    def jsonable(self):
        return {
            'id': self.id,
            'grav_hash': self.grav_hash,
            'name': self.name
        }


class Follow(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    init_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    respond_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    init = db.relationship('User', foreign_keys=[init_id])
    respond = db.relationship('User', foreign_keys=[respond_id])


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(256))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator_login = db.Column(db.String(50))
    creator = db.relationship('User', backref='posts')
    login = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    photo = db.Column(db.BLOB)
    photo_type = db.Column(db.String(50))

    @property
    def jsonable(self):
        return {
            'post_id': self.id,
            'timestamp': str(self.timestamp),
            'has_photo': self.photo is not None
        }


User.follow = db.relationship('User', secondary='follow', primaryjoin=User.id==Follow.init_id,
                              secondaryjoin=User.id==Follow.respond_id)


db.create_all(app=app)