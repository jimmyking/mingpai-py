#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import OrderType,IssueType,Order,Area,OrderProcess
from datetime import datetime
from .. import db
from . import order

#订单处理中心
@order.route('/')
@login_required
def orders():
	ordertypes = OrderType.query.order_by('id').all()
	issuetypes = IssueType.query.order_by('id').all()
	areas = Area.query.order_by('id').all()
	orders = Order.query.filter_by(is_delete=0).order_by('id').all()
	return render_template('order/index.html',ordertypes=ordertypes,issuetypes=issuetypes,orders=orders,areas=areas)

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
		            start_level=start_level,end_level=end_level,now_level=start_level, \
		            wangwang=wangwang,qq=qq,mobile=mobile,amount=amount, \
		            paytype=paytype,memo=memo)
	order.status_id=1
	order.create_man = current_user.id
	order.init_order_no()
	db.session.add(order)
	db.session.commit()

	OrderProcess.save(order.id,current_user.id,"新增订单")
	return redirect(url_for('order.orders'))

@order.route('/update_order',methods=['POST'])
@login_required
def update_order():
	gid = request.form['id']
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
	Order.query.filter_by(id=gid).update({Order.type_id:type_id,Order.area_id:area_id,Order.acter_name:acter_name, \
										  Order.acter_account:acter_account,Order.acter_password:acter_password, \
										  Order.start_level:start_level,Order.end_level:end_level,Order.wangwang:wangwang, \
										  Order.qq:qq,Order.mobile:mobile,Order.amount:amount,Order.paytype:paytype, \
										  Order.memo:memo,Order.update_man:current_user.id,Order.update_date:datetime.now()})
	db.session.commit()
	OrderProcess.save(gid,current_user.id,"修改订单")
	return redirect(url_for('order.orders'))

@order.route('/del_order',methods=['POST'])
@login_required
def del_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.is_delete:1},synchronize_session=False)
	db.session.commit()
	return redirect(url_for('order.orders'))


@order.route('/check_order',methods=['POST'])
@login_required
def check_order():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.status_id:2})
	db.session.commit()
	return redirect(url_for('order.orders'))

@order.route('/_get_order/<gid>')
def get_order(gid):
	order = Order.query.filter_by(id=gid).first()
	return jsonify(order.to_json())








#订单回收站
@order.route('/trash')
@login_required
def trash():
	orders = Order.query.filter_by(is_delete=1).order_by('id').all()
	return render_template('order/trash.html',orders=orders)

@order.route('/undel',methods=['POST'])
@login_required
def undel_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.is_delete:0},synchronize_session=False)
	db.session.commit()
	return redirect(url_for('order.trash'))

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



