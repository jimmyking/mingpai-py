#coding=utf-8 
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user,logout_user, login_required
from ..models import User
from . import auth

@auth.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()

		if user is not None and user.verify_password(request.form['password']):
			login_user(user)
			return redirect(request.args.get('next') or url_for('main.index'))

		#flash('用户名或密码错误')
	return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('auth.login'))