#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import OrderType,IssueType,Order,Area,OrderProcess,OrderStatus
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
	status = OrderStatus.query.order_by('id').all()
	order_query = Order.query.filter_by(is_delete=0)
	order_no = request.args.get('order_no')
	if order_no:
		order_query = order_query.filter_by(order_no=order_no)
	acter_name = request.args.get('acter_name')
	if acter_name:
		order_query = order_query.filter_by(acter_name=acter_name)
	area_id = request.args.get('area_id')
	if area_id and area_id !='0':
		order_query = order_query.filter_by(area_id=area_id)
	status_id = request.args.get('status_id')
	if status_id and status_id !='0':
		order_query = order_query.filter_by(status_id=status_id)
	type_id = request.args.get('type_id')
	if type_id and type_id !='0':
		order_query = order_query.filter_by(type_id=type_id)
	is_issue = request.args.get('is_issue')
	if is_issue and is_issue =='1':
		order_query = order_query.filter_by(is_issue=1)

	orders = order_query.order_by('id').all()


	return render_template('order/index.html',ordertypes=ordertypes,issuetypes=issuetypes,orders=orders,areas=areas,status=status)

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
	Order.query.filter_by(id=oid).update({Order.status_id:2,Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	OrderProcess.save(oid,current_user.id,"审核订单")
	return redirect(url_for('order.orders'))

@order.route('/bug_order',methods=['POST'])
@login_required
def bug_order():
	oid = request.form['oid']
	issue_type = request.form['issue_type']
	issue_memo = request.form['issue_memo']
	Order.query.filter_by(id=oid).update({Order.is_issue:1,Order.issue_id:issue_type,Order.issue_memo:issue_memo, \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()

	OrderProcess.save(oid,current_user.id,u"标记为异常订单 异常信息为: %s" %issue_memo)
	return redirect(url_for('order.orders'))

@order.route('/unbug_order',methods=['POST'])
@login_required
def unbug_order():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.is_issue:0,Order.issue_id:None,Order.issue_memo:"", \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	OrderProcess.save(oid,current_user.id,"解除异常")
	return redirect(url_for('order.orders'))

@order.route('/wait_task',methods=['POST'])
@login_required
def wait_task():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.status_id:6},synchronize_session=False)
	for oid in gids.split(','):
		OrderProcess.save(oid,current_user.id,"修改状态至转任务组")
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




