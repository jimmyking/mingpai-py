#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required
from ..models import WarningType
from .. import db
from . import warning

#订单类型管理
@warning.route('/')
@login_required
def index():
	ordertypes = WarningType.query.order_by('id').all()
	return render_template('warning/index.html',ordertypes=ordertypes)

@warning.route('/add_ordertype',methods=['POST'])
@login_required
def add_ordertype():
	ordertype = WarningType(name=request.form['name'],color=request.form['color'])
	db.session.add(ordertype)
	db.session.commit()
	return redirect(url_for('warning.index'))

@warning.route('/del_ordertype',methods=['POST'])
@login_required
def del_ordertype():
	gids = request.form['gids']
	WarningType.query.filter(WarningType.id.in_(gids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('warning.index'))

@warning.route('/update_ordertype',methods=['POST'])
@login_required
def update_ordertype():
	gid = request.form['id']
	name = request.form['name']
	color = request.form['color']
	WarningType.query.filter_by(id=gid).update({WarningType.name:name, WarningType.color:color})
	db.session.commit()
	return redirect(url_for('warning.index'))

@warning.route('/_get_ordertype/<gid>')
def get_ordertype(gid):
	ordertype = WarningType.query.filter_by(id=gid).first()
	return jsonify(ordertype.to_json())



