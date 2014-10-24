#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required
from ..models import OrderType,IssueType
from .. import db
from . import dic

#订单类型管理
@dic.route('/ordertypes')
@login_required
def ordertypes():
	ordertypes = OrderType.query.order_by('id').all()
	return render_template('dic/order_types.html',ordertypes=ordertypes)

@dic.route('/add_ordertype',methods=['POST'])
@login_required
def add_ordertype():
	ordertype = OrderType(name=request.form['name'],color=request.form['color'])
	db.session.add(ordertype)
	db.session.commit()
	return redirect(url_for('dic.ordertypes'))

@dic.route('/del_ordertype',methods=['POST'])
@login_required
def del_ordertype():
	gids = request.form['gids']
	OrderType.query.filter(OrderType.id.in_(gids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('dic.ordertypes'))

@dic.route('/update_ordertype',methods=['POST'])
@login_required
def update_ordertype():
	gid = request.form['id']
	name = request.form['name']
	color = request.form['color']
	OrderType.query.filter_by(id=gid).update({OrderType.name:name, OrderType.color:color})
	db.session.commit()
	return redirect(url_for('dic.ordertypes'))

@dic.route('/_get_ordertype/<gid>')
def get_ordertype(gid):
	ordertype = OrderType.query.filter_by(id=gid).first()
	return jsonify(ordertype.to_json())


#异常类型管理
@dic.route('/issuetypes')
@login_required
def issuetypes():
	issuetypes = IssueType.query.order_by('id').all()
	return render_template('dic/issue_types.html',issuetypes=issuetypes)

@dic.route('/add_issuetype',methods=['POST'])
@login_required
def add_issuetype():
	issuetype = IssueType(name=request.form['name'])
	db.session.add(issuetype)
	db.session.commit()
	return redirect(url_for('dic.issuetypes'))

@dic.route('/del_issuetype',methods=['POST'])
@login_required
def del_issuetype():
	gids = request.form['gids']
	IssueType.query.filter(IssueType.id.in_(gids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('dic.issuetypes'))

@dic.route('/update_issuetype',methods=['POST'])
@login_required
def update_issuetype():
	gid = request.form['id']
	name = request.form['name']
	IssueType.query.filter_by(id=gid).update({IssueType.name:name})
	db.session.commit()
	return redirect(url_for('dic.issuetypes'))

@dic.route('/_get_issuetype/<gid>')
def get_issuetype(gid):
	issuetype = IssueType.query.filter_by(id=gid).first()
	return jsonify(issuetype.to_json())




