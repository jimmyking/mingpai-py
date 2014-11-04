#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request,Response
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from ..models import GroupTask,OrderTask,OrderGroupTask,IssueType,WarningType
from datetime import datetime
from .. import db
from . import team
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers

@team.route('/')
@login_required
def index():
	#teams =  OrderGroup.query.filter_by(group_type=0).filter(OrderGroup.status_id.in_([3,4])).all()
	teams =  OrderGroup.query.filter_by(group_type=0)
	areas = Area.query.order_by('id').all()
	issuetypes = IssueType.query.order_by('id').all()
	warninges = WarningType.query.order_by('id').all()
	tasks = GroupTask.query.filter_by(type=0).order_by('id').all()

	start_date = request.args.get('start-date')
	if start_date:
		teams = teams.filter(db.cast(OrderGroup.name,db.DATE)>=start_date)
	end_date = request.args.get('end_date')
	if end_date:
		teams = teams.filter(db.cast(OrderGroup.name,db.DATE)<end_date)

	status_id = request.args.get('status_id')
	if status_id == '1':
		teams = teams.filter(OrderGroup.status_id.in_([5]))
	else:
		teams = teams.filter(OrderGroup.status_id.in_([3,4]))
	area_id = request.args.get('area_id')
	if area_id and area_id != '0':
		teams = teams.filter_by(area_id=area_id)
	
	
	teams = teams.order_by('id').all()
	return render_template('team/index.html',teams=teams,tasks=tasks,areas=areas,issuetypes=issuetypes,warninges=warninges)

@team.route('/add_team',methods=['POST'])
@login_required
def add_team():
	oids = request.form['group-order-ids']
	area_id = request.form['group-area-id']
	name = request.form['group-name']
	target = request.form['group-target']
	row = db.session.query(OrderGroup.id,db.func.count('*').label('count')). \
					 filter(OrderGroup.name==name). \
					 filter(OrderGroup.area_id==area_id). \
					 filter(OrderGroup.group_type==0).first()
	no = row.count+1
	team = OrderGroup(group_type=0,area_id=area_id,name=name,no=no,target=target,status_id=3, \
		             create_man=current_user.id)
	db.session.add(team)
	db.session.commit()
	OrderGroupProcess.save(team.id,current_user.id,"创建团练分组")

	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.group_id:team.id,Order.status_id:3, \
		                                                      Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()

	area = Area.query.filter_by(id=area_id).first()

	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,(u"分配到: %s%s%d组" %(name,area.name,no)))

	return redirect(request.referrer)

@team.route('/start_team',methods=['POST'])
@login_required
def start_team():
	tid = request.form['tid']
	OrderGroup.query.filter_by(id=tid).update({OrderGroup.status_id:4,OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(tid,current_user.id,"开始团练")
	Order.query.filter_by(group_id=tid).update({Order.status_id:4, \
		                                            Order.update_man:current_user.id, \
		                                            Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=tid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,"开始团练")
	db.session.commit()
	return redirect(url_for('team.index'))

@team.route('/stop_team',methods=['POST'])
@login_required
def stop_team():
	tid = request.form['tid']
	OrderGroup.query.filter_by(id=tid).update({OrderGroup.status_id:5,OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(tid,current_user.id,"团练完成")
	Order.query.filter_by(group_id=tid).update({Order.status_id:5, \
		                                            Order.update_man:current_user.id, \
		                                            Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=tid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,"团练完成")
	db.session.commit()
	return redirect(url_for('team.index'))

@team.route('/update_level',methods=['POST'])
@login_required
def update_level():
	tid = request.form['tid']
	team = OrderGroup.query.filter_by(id=tid).first()
	if team.status_id !=4:
		return redirect(url_for('team.index'))
	level = request.form['level']
	OrderGroup.query.filter_by(id=tid).update({OrderGroup.now_level:level,OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(tid,current_user.id,u"更新进度到 %s" % level)
	Order.query.filter_by(group_id=tid).update({Order.now_level:level, \
		                                            Order.update_man:current_user.id, \
		                                            Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=tid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,u"更新进度到 %s" % level)
	db.session.commit()
	return redirect(url_for('team.index'))


@team.route('/update_task',methods=['POST'])
@login_required
def update_task():
	gid = request.form['group_id']
	tid = request.form['task_id']
	team = OrderGroup.query.filter_by(id=gid).first()
	task = GroupTask.query.filter_by(id=tid).first()
	if team.status_id !=4:
		return redirect(url_for('team.index'))
	
	OrderGroup.query.filter_by(id=gid).update({OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(gid,current_user.id,u"完成任务 %s" % task.name)
	OrderGroupTask.save(gid,tid,current_user.id)
	Order.query.filter_by(group_id=gid).update({Order.update_man:current_user.id, \
		                                        Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=gid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,u"完成任务 %s" % task.name)
		OrderTask.save(order.id,tid,current_user.id)
	db.session.commit()
	return redirect(url_for('team.index'))

@team.route('/out_team',methods=['POST'])
@login_required
def out_team():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.group_id:None,Order.status_id:2,Order.update_man:current_user.id, \
		                                        Order.update_date:datetime.now()},synchronize_session=False)
	OrderProcess.save(oid,current_user.id,"订单踢出团队")
	db.session.commit()
	return redirect(url_for('team.index'))
	


@team.route('/_get_team_orders/<tid>')
@login_required
def get_team_orders(tid):
	orders = Order.query.filter_by(group_id=tid).all()
	return render_template('team/orders.html',orders=orders)

@team.route('/_get_team/<tid>')
@login_required
def get_team(tid):
	team = OrderGroup.query.filter_by(id=tid).first()
	return jsonify(team.to_json())

@team.route('/__get_available_team/<type>')
@login_required
def get_available_team(type):
	status = [3,4]
	if type == '1':
		status = [7,8]
	teams =  OrderGroup.query.filter_by(group_type=type).filter(OrderGroup.status_id.in_(status)).all()
	return render_template('team/teams.html',teams=teams)


@team.route('/export')
def export():
	tid = request.args.get('tid')
	orders = Order.query.filter_by(group_id=tid).all()
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
	sheet.write(0,15,u'创建时间')

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
		sheet.write(index,15,str(order.create_date))
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