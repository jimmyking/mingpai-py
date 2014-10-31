from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from . import main
from ..models import User,Role
from .. import db


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@main.route('/users')
@login_required
def users():
	users = User.query.order_by('id').all()
	roles = Role.query.order_by('id').all()
	return render_template('users.html',users=users,roles=roles)

@main.route('/add_user',methods=['POST'])
@login_required
def add_user():
	user = User(username=request.form['username'],name=request.form['name'],password=request.form['password'],role_id=request.form['role_id'])
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('main.users'))

@main.route('/del_user',methods=['POST'])
@login_required
def delete_user():
	uids = request.form['uids']
	User.query.filter(User.id.in_(uids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('main.users'))

@main.route('/update_user',methods=['POST'])
@login_required
def update_user():
	uid = request.form['id']
	username = request.form['username']
	name = request.form['name']
	role_id = request.form['role_id']
	User.query.filter_by(id=uid).update({User.username:username,User.name:name,User.role_id:role_id})
	db.session.commit()
	return redirect(url_for('main.users'))

@main.route('/_get_user/<uid>')
def get_user(uid):
	user = User.query.filter_by(id=uid).first()
	return jsonify(user.to_json())



