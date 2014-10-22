from flask import render_template, session, redirect, url_for, current_app
from flask.ext.login import login_required
from . import main
from ..models import User
#from .. import db


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@main.route('/users')
@login_required
def users():
	users = User.query.order_by('id').all()
	return render_template('users.html',users=users)


