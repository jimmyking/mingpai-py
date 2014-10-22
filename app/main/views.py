from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required
from . import main
from ..models import User
from .. import db


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@main.route('/users')
@login_required
def users():
	users = User.query.order_by('id').all()
	return render_template('users.html',users=users)

@main.route('/add_user',methods=['POST'])
@login_required
def add_user():
	user = User(username=request.form['username'],password=request.form['password'])
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('main.users'))

@main.route('/_get_user/<uid>')
def get_user(uid):
	user = User.query.filter_by(id=uid).first()
	return jsonify(user.to_json())

