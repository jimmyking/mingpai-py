from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db,login_manager
from datetime import datetime,date


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    #users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))

    role = db.relationship("Role", backref=db.backref("user", order_by=id))

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
            'name': self.name,
            'role_id': self.role_id
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

class OrderGroup(db.Model):
    __tablename__ = 'order_groups'
    id = db.Column(db.Integer, primary_key=True)
    group_type = db.Column(db.Integer)
    area_id = db.Column(db.Integer,db.ForeignKey('areas.id'))
    name = db.Column(db.String(64))
    no = db.Column(db.Integer)
    target = db.Column(db.String(64))
    now_level = db.Column(db.Integer,default=0) 
    status_id = db.Column(db.Integer,db.ForeignKey('order_status.id'))
    create_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime,default=datetime.now,index=True)
    update_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    update_date = db.Column(db.DateTime,default=datetime.now)

    status = db.relationship("OrderStatus", backref=db.backref("group_status", order_by=id))
    area = db.relationship("Area", backref=db.backref("group_areas", order_by=id))
    tasks = db.relationship('OrderGroupTask', backref='group_tasks',lazy='dynamic')

    orders = db.relationship('Order', backref=db.backref('order_groups'),lazy='dynamic')

    def __repr__(self):
        return '<OrderGrouop %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'type': self.group_type,
            'area_id': self.area.id,
            'area_name': self.area.name,
            'name': self.name,
            'no': self.no,
            'target': self.target,
            'now_level': self.now_level,
        }

    def to_task_json(self):
        return {
            'id': self.id,
            'type': self.group_type,
            'name': self.name,
            'no': self.no,
            'target': self.target,
        }

class OrderGroupTask(db.Model):
    __tablename__ = 'order_group_tasks'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer,db.ForeignKey('order_groups.id'))
    task_id = db.Column(db.Integer,db.ForeignKey('group_tasks.id'))
    create_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime,default=datetime.now,index=True)

    task = db.relationship("GroupTask", backref=db.backref("group_task", order_by=id))

    def __repr__(self):
        return '<OrderGroupTask %r>' % self.id

    @classmethod
    def save(cls,gid,tid,oper):
        task = OrderGroupTask(group_id=gid,task_id=tid,create_man=oper,create_date=datetime.now())
        db.session.add(task)
        db.session.commit()

class OrderGroupProcess(db.Model):
    __tablename__ = 'order_group_process'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer,db.ForeignKey('order_groups.id'))
    oper = db.Column(db.Integer,db.ForeignKey('users.id'))
    oper_time = db.Column(db.DateTime,default=datetime.now)
    remark = db.Column(db.String(128))    

    def __repr__(self):
        return '<OrderGroupProcess %r>' % self.id

    def to_json(self):
        return {
            'id': self.id,
            'oper': self.oper,
            'oper_time': self.oper_time,
            'remark': self.remark,
        }

    @classmethod
    def save(cls,oid,oper,remark):
        process = OrderGroupProcess(group_id=oid,oper=oper,oper_time=datetime.now(),remark=remark)
        db.session.add(process)
        db.session.commit()


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
    end_level = db.Column(db.Integer,default=0)
    now_level = db.Column(db.Integer,default=0)
    wangwang = db.Column(db.String(128))
    qq = db.Column(db.String(64))
    mobile = db.Column(db.String(64))
    amount = db.Column(db.String(64))
    paytype = db.Column(db.String(128))
    memo = db.Column(db.String(128))
    is_issue = db.Column(db.Integer,default=0)
    is_delete = db.Column(db.Integer,default=0)
    issue_id = db.Column(db.Integer,db.ForeignKey('issue_types.id'))
    issue_memo = db.Column(db.String(128))
    create_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime,default=datetime.now,index=True)
    update_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    update_date = db.Column(db.DateTime,default=datetime.now)
    group_id = db.Column(db.Integer,db.ForeignKey('order_groups.id'))

    order_type = db.relationship("OrderType", backref=db.backref("orders", order_by=id))
    order_status = db.relationship("OrderStatus", backref=db.backref("order_status", order_by=id))
    area = db.relationship("Area", backref=db.backref("areas", order_by=id))


    

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

    def init_order_no(self):
        row = db.session.query(Order.id,db.func.count('*').label('count')).filter(db.cast(Order.create_date,db.DATE)==date.today()).first()
        count = row.count+1
        self.order_no = datetime.now().strftime('%Y%m%d')+str(count).zfill(5)


class OrderTask(db.Model):
    __tablename__ = 'order_tasks'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('orders.id'))
    task_id = db.Column(db.Integer,db.ForeignKey('group_tasks.id'))
    create_man = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime,default=datetime.now,index=True)

    def __repr__(self):
        return '<OrderGroupTask %r>' % self.id

    @classmethod
    def save(cls,oid,tid,oper):
        task = OrderTask(order_id=oid,task_id=tid,create_man=oper,create_date=datetime.now())
        db.session.add(task)
        db.session.commit()

class OrderProcess(db.Model):
    __tablename__ = "order_process"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('orders.id'))
    oper = db.Column(db.Integer,db.ForeignKey('users.id'))
    oper_time = db.Column(db.DateTime,default=datetime.now)
    remark = db.Column(db.String(128))    

    oper_man = db.relationship("User", backref=db.backref("users", order_by=id))


    def __repr__(self):
        return '<OrderProcess %r>' % self.id

    def to_json(self):
        return {
            'id': self.id,
            'oper': self.oper,
            'oper_time': self.oper_time,
            'remark': self.remark,
        }

    @classmethod
    def save(cls,oid,oper,remark):
        process = OrderProcess(order_id=oid,oper=oper,oper_time=datetime.now(),remark=remark)
        db.session.add(process)
        db.session.commit()

class GroupTask(db.Model):
    __tablename__ = "group_tasks"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<GroupTask %r>' % self.id

    def to_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
        }

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
