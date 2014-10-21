from flask import render_template, session, redirect, url_for, current_app
from . import main
#from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.before_request
def before_request():
	print "hello main"
