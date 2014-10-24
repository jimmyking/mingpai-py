#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required
from ..models import OrderType,IssueType,Order
from .. import db
from . import order

@order.route('/')
@login_required
def orders():
	ordertypes = OrderType.query.order_by('id').all()
	issuetypes = IssueType.query.order_by('id').all()
	orders = Order.query.order_by('id').all()
	return render_template('order/index.html',ordertypes=ordertypes,issuetypes=issuetypes,orders=orders)

@order.route('/add_order',methods=['POST'])
@login_required
def add_order():
	type_id = request.form['type_id']
	area_id = request.form['area_id']
	acter_name = request.form['acter_name']
	acter_account = request.form['acter_account']
	acter_password = request.form['acter_password']
	start_level = request.form['start_level']
	end_level = request.form['end_level']
	wangwang = request.form['wangwang']
	qq = request.form['qq']
	mobile = request.form['mobile']
	amount = request.form['amount']
	paytype = request.form['paytype']
	memo = request.form['memo']
	order = Order(type_id=int(type_id),area_id=int(area_id),acter_name=acter_name, \
		            acter_account=acter_account,acter_password=acter_password, \
		            start_levhel=start_level,end_level=end_level,now_level=start_level, \
		            wangwang=wangwang,qq=qq,mobile=mobile,amount=amount, \
		            paytype=paytype,memo=memo)
	order.status_id=1
	order.init_order_no()
	db.session.add(order)
	db.session.commit()
	return redirect(url_for('order.orders'))

@order.route('/del_order',methods=['POST'])
@login_required
def del_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.is_delete:1})
	db.session.commit()
	return redirect(url_for('order.orders'))


"""
from datetime import date
from sqlalchemy import cast, DATE
Match.query.filter(cast(Match.date_time_field, DATE)==date.today()).all()


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
"""



