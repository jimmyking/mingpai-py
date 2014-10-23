from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db,login_manager
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
        }

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Game %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'username': self.name,
        }

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    def __repr__(self):
        return '<Area %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'username': self.name,
        }

class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))

    def __repr__(self):
        return '<Server %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'username': self.name,
        }

class OrderType(db.Model):
    __tablename__ = 'order_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<OrderType %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class IssueType(db.Model):
    __tablename__ = 'issue_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<IssueType %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
        }

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
