from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db,login_manager
from datetime import datetime,date


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
    color = db.Column(db.String(64))

    def __repr__(self):
        return '<OrderType %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
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

class OrderStatus(db.Model):
    __tablename__ = 'order_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    def __repr__(self):
        return '<OrderStatus %r>' % self.name


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(64),unique=True, index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('order_types.id'))
    status_id = db.Column(db.Integer,db.ForeignKey('order_status.id'))
    area_id = db.Column(db.Integer,db.ForeignKey('areas.id'))
    acter_name = db.Column(db.String(128),index=True)
    acter_account = db.Column(db.String(128),index=True)
    acter_password = db.Column(db.String(128))
    start_level = db.Column(db.Integer)
    end_level = db.Column(db.Integer)
    now_level = db.Column(db.Integer)
    wangwang = db.Column(db.String(128))
    qq = db.Column(db.String(64))
    mobile = db.Column(db.String(64))
    amount = db.Column(db.String(64))
    paytype = db.Column(db.String(128))
    memo = db.Column(db.String(128))
    is_issue = db.Column(db.Integer)
    issue_id = db.Column(db.Integer,db.ForeignKey('issue_types.id'))
    issue_memo = db.Column(db.String(128))
    create_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime,default=datetime.now,index=True)
    update_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    update_date = db.Column(db.DateTime,default=datetime.now)

    #def init_order_no(self):
     #   db.session.query(Order.id,db.func.count('*')).filter(Order.create_date=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.order_no

    def to_json(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'type_id': self.type_id,
            'status_id': self.status_id,
            'area_id': self.area_id,
            'acter_name': self.acter_name,
            'acter_account': self.acter_account,
            'acter_password': self.acter_password,
            'start_level': self.start_level,
            'end_level': self.end_level,
            'now_level': self.now_level,
            'wangwang': self.wangwang,
            'qq': self.qq,
            'mobile': self.mobile,
            'amount': self.amount,
            'paytype': self.paytype,
            'memo': self.memo,
        }

    @classmethod
    def init_order_no(cls):
        db.session.query(Order.id,db.func.count('*').label('count')).filter(db.cast(Order.create_date,db.DATE)==date.today()).first()

#        Match.query.filter(cast(Match.date_time_field, DATE)==date.today()).all()


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
