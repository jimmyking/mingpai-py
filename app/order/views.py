#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request,Response
from flask.ext.login import login_required,current_user
from ..models import OrderType,IssueType,Order,Area,OrderProcess,OrderStatus,OrderGroup,WarningType,OrderWarning
from datetime import datetime
from .. import db
from . import order
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers

#订单处理中心
@order.route('/')
@login_required
def orders():
	ordertypes = OrderType.query.order_by('id').all()
	issuetypes = IssueType.query.order_by('id').all()
	warninges = WarningType.query.order_by('id').all()
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
	else:
		order_query = order_query.filter(Order.status_id != 11)
	type_id = request.args.get('type_id')
	if type_id and type_id !='0':
		order_query = order_query.filter_by(type_id=type_id)
	is_issue = request.args.get('is_issue')
	if is_issue:
		order_query = order_query.filter_by(is_issue=is_issue)
	wangwang = request.args.get('wangwang')
	if wangwang:
		order_query = order_query.filter_by(wangwang=wangwang)
	mobile = request.args.get('mobile')
	if mobile:
		order_query = order_query.filter_by(mobile=mobile)


	orders = order_query.order_by('id desc').all()


	return render_template('order/index.html',ordertypes=ordertypes,issuetypes=issuetypes,orders=orders,areas=areas,status=status,warninges=warninges)

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
	warning_type = request.form['warning_type']
	taobao_date = request.form['taobao_date']
	order = Order(type_id=int(type_id),area_id=int(area_id),acter_name=acter_name, \
		            acter_account=acter_account,acter_password=acter_password, \
		            start_level=start_level,end_level=end_level,now_level=start_level, \
		            wangwang=wangwang,qq=qq,mobile=mobile,amount=amount, \
		            paytype=paytype,memo=memo,warning_type=warning_type,taobao_date=taobao_date)
	order.status_id=1
	order.create_man = current_user.id
	order.init_order_no()
	db.session.add(order)
	db.session.commit()
	OrderWarning.save(order.id,warning_type,memo,current_user.id)
	OrderProcess.save(order.id,current_user.id,"新增订单")
	return redirect(request.referrer)

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
	taobao_date = request.form['taobao_date']
	Order.query.filter_by(id=gid).update({Order.type_id:type_id,Order.area_id:area_id,Order.acter_name:acter_name, \
										  Order.acter_account:acter_account,Order.acter_password:acter_password, \
										  Order.start_level:start_level,Order.end_level:end_level,Order.wangwang:wangwang, \
										  Order.qq:qq,Order.mobile:mobile,Order.amount:amount,Order.paytype:paytype, \
										  Order.memo:memo,Order.update_man:current_user.id,Order.update_date:datetime.now(),Order.taobao_date:taobao_date})
	db.session.commit()
	OrderProcess.save(gid,current_user.id,"修改订单")
	return redirect(request.referrer)

@order.route('/del_order',methods=['POST'])
@login_required
def del_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.is_delete:1},synchronize_session=False)
	db.session.commit()
	
	return redirect(request.referrer)


@order.route('/check_order',methods=['POST'])
@login_required
def check_order():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.status_id:2,Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	OrderProcess.save(oid,current_user.id,"审核订单")
	return redirect(request.referrer)

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
	return redirect(request.referrer)

@order.route('/unbug_order',methods=['POST'])
@login_required
def unbug_order():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.is_issue:0,Order.issue_id:None,Order.issue_memo:"", \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	OrderProcess.save(oid,current_user.id,"解除异常")
	return redirect(request.referrer)

@order.route('/wait_task',methods=['POST'])
@login_required
def wait_task():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.status_id:6},synchronize_session=False)
	for oid in gids.split(','):
		OrderProcess.save(oid,current_user.id,"修改状态至转任务组")
	db.session.commit()
	
	return redirect(request.referrer)

@order.route('/add_warning',methods=['POST'])
@login_required
def add_warning():
	oid = request.form['oid']
	warning_type = request.form['warning_type']
	content = request.form['content']

	Order.query.filter_by(id=oid).update({Order.warning_type:warning_type,Order.update_date:datetime.now(),Order.update_man:current_user.id},synchronize_session=False)
	db.session.commit()
	OrderWarning.save(oid,warning_type,content,current_user.id)
	
	return redirect(request.referrer)


@order.route('/complete_order',methods=['POST'])
@login_required
def complete_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.status_id:10},synchronize_session=False)
	for oid in gids.split(','):
		OrderProcess.save(oid,current_user.id,"修改状态至已完成")
	db.session.commit()
	
	return redirect(request.referrer)

@order.route('/back_order_to_start',methods=['POST'])
@login_required
def back_order_to_start():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.status_id:1,Order.group_id:None,Order.team_id:None},synchronize_session=False)
	for oid in gids.split(','):
		OrderProcess.save(oid,current_user.id,"修改状态至新订单")
	db.session.commit()
	
	return redirect(request.referrer)

@order.route('/notification_order',methods=['POST'])
@login_required
def notification_order():
	gids = request.form['gids']
	Order.query.filter(Order.id.in_(gids.split(','))).update({Order.status_id:11},synchronize_session=False)
	for oid in gids.split(','):
		OrderProcess.save(oid,current_user.id,"修改状态至已通知")
	db.session.commit()
	
	return redirect(request.referrer)

@order.route('/to_group',methods=['POST'])
def to_group():
	oid = request.form['oid'];
	tid = request.form['tid'];

	

	group = OrderGroup.query.filter_by(id=tid).first()

	Order.query.filter_by(id=oid).update({Order.group_id:tid,Order.status_id:group.status_id, \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	if group.group_type == 0:
		OrderProcess.save(oid,current_user.id,u"订单加入 %s %s %s组" %(group.name,group.area.name,group.no))
	else:
		OrderProcess.save(oid,current_user.id,u"订单加入 %s %s组 %s号机" %(group.name,group.no,group.target))
	return redirect(request.referrer)


@order.route('/_get_order/<gid>')
def get_order(gid):
	order = Order.query.filter_by(id=gid).first()
	return jsonify(order.to_json())





@order.route('/export')
def export():
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
	response=Response()
	response.status_code=200
	workbook=xlwt.Workbook()
	sheet = workbook.add_sheet('A Test Sheet')
	sheet.write(0,0,u'单号')
	sheet.write(0,1,u'类型')
	sheet.write(0,2,u'状态')
	sheet.write(0,3,u'区服')
	sheet.write(0,4,u'角色')
	sheet.write(0,5,u'账号')
	sheet.write(0,6,u'密码')
	sheet.write(0,7,u'起点')
	sheet.write(0,8,u'需求')
	sheet.write(0,9,u'当前')
	sheet.write(0,10,u'旺旺')
	sheet.write(0,11,u'QQ号')
	sheet.write(0,12,u'电话')
	sheet.write(0,13,u'金额')
	sheet.write(0,14,u'支付')

	index = 1;
	for order in orders:
		sheet.write(index,0,order.order_no)
		sheet.write(index,1,order.order_type.name)
		sheet.write(index,2,order.order_status.name)
		sheet.write(index,3,order.area.name)
		sheet.write(index,4,order.acter_name)
		sheet.write(index,5,order.acter_account)
		sheet.write(index,6,order.acter_password)
		sheet.write(index,7,order.start_level)
		sheet.write(index,8,order.end_level)
		sheet.write(index,9,order.now_level)
		sheet.write(index,10,order.wangwang)
		sheet.write(index,11,order.qq)
		sheet.write(index,12,order.mobile)
		sheet.write(index,13,order.amount)
		sheet.write(index,14,order.paytype)
		index = index+1;


	output = StringIO.StringIO()
	workbook.save(output)
	response.data = output.getvalue()

	filename = 'export.xls'
	mimetype_tuple = mimetypes.guess_type(filename)

	response_headers = Headers({
			'Pragma' : "public",
			'Expires' : '0',
			'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
			'Cache-Control': 'private',
			'Content-Type': mimetype_tuple[0],
			'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
			'Content-Transfer-Encoding': 'binary',
			'Content-Length': len(response.data)
		})

	if not mimetype_tuple[1] is None:
		response.update({
				'Content-Encoding' : mimetype_tuple[1]
			})

	response.headers = response_headers

	return response



@order.route('/__get_info/<oid>')
def get_info(oid):
	order = Order.query.filter_by(id=oid).first()
	orderprocess = OrderProcess.query.filter_by(order_id=oid).order_by('id').all()
	warninges = OrderWarning.query.filter_by(order_id=oid).order_by('id').all()
	return render_template('order/info.html',order=order,orderprocess=orderprocess,warninges=warninges)

@order.route('/__get_log/<oid>')
def get_log(oid):
	orderprocess = OrderProcess.query.filter_by(order_id=oid).order_by('id').all()
	warninges = OrderWarning.query.filter_by(order_id=oid).order_by('id').all()

	return render_template('order/logs.html',orderprocess=orderprocess,warninges=warninges)

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




