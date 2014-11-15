#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request,Response
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from ..models import GroupTask,OrderTask,OrderTeam,IssueType,WarningType,OrderWarning
from datetime import datetime
from .. import db
from . import task
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers

@task.route('/')
@login_required
def index():
	teams =  OrderTeam.query

	section = request.args.get('section')
	if section:
		teams = teams.filter(OrderTeam.section==section)
	no = request.args.get('no')
	if no:
		teams = teams.filter(OrderTeam.no==no)
	status_id = request.args.get('status_id')
	if status_id == '1':
		teams = teams.filter(OrderTeam.status_id.in_([9]))
	else:
		teams = teams.filter(OrderTeam.status_id.in_([7,8]))
	start_date = request.args.get('start-date')
	if start_date:
		teams = teams.filter(db.cast(OrderTeam.name,db.DATE)>=start_date)
	end_date = request.args.get('end_date')
	if end_date:
		teams = teams.filter(db.cast(OrderTeam.name,db.DATE)<end_date)

	teams = teams.order_by('id').all()
	orders = Order.query.filter_by(status_id=6).order_by('id desc').all()
	tasks = GroupTask.query.filter_by(type=1).order_by('id desc').all()
	issuetypes = IssueType.query.order_by('id').all()
	warninges = WarningType.query.order_by('id').all()
	return render_template('task/index.html',teams=teams,orders=orders,tasks=tasks,issuetypes=issuetypes,warninges=warninges)

@task.route('/add_team',methods=['POST'])
@login_required
def add_team():
	oids = request.form['oids']
	name = request.form['name']
	no = request.form['no']
	target = request.form['target']
	team = OrderTeam(group_type=1,name=name,section=no,no=target,status_id=7, \
		             create_man=current_user.id)
	db.session.add(team)
	db.session.commit()

	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.team_id:team.id,Order.status_id:7, \
		                                                      Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()
	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,(u"分配到: %s  %s组%s号机" %(name,no,target)))

	return redirect(request.referrer)


@task.route('/start_task',methods=['POST'])
@login_required
def start_task():
	tid = request.form['tid']
	OrderTeam.query.filter_by(id=tid).update({OrderTeam.status_id:8,OrderTeam.update_man:current_user.id, \
											   OrderTeam.update_date:datetime.now()},synchronize_session=False)
	Order.query.filter_by(team_id=tid).update({Order.status_id:8, \
		                                            Order.update_man:current_user.id, \
		                                            Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=tid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,"开始任务")
	db.session.commit()
	return redirect(url_for('task.index'))

@task.route('/stop_task',methods=['POST'])
@login_required
def stop_task():
	tid = request.form['tid']
	OrderTeam.query.filter_by(id=tid).update({OrderTeam.status_id:9,OrderTeam.update_man:current_user.id, \
											   OrderTeam.update_date:datetime.now()},synchronize_session=False)
	Order.query.filter_by(team_id=tid).update({Order.status_id:9, \
		                                            Order.update_man:current_user.id, \
		                                            Order.update_date:datetime.now()},synchronize_session=False)
	orders = Order.query.filter_by(group_id=tid).all()
	for order in orders:
		OrderProcess.save(order.id,current_user.id,"任务完成")
	db.session.commit()
	return redirect(url_for('task.index'))


@task.route('/update_task',methods=['POST'])
@login_required
def update_task():
	gid = request.form['group_id']
	tid = request.form['task_id']
	team = OrderGroup.query.filter_by(id=gid).first()
	task = GroupTask.query.filter_by(id=tid).first()
	if team.status_id !=8:
		return redirect(url_for('task.index'))
	
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
	return redirect(url_for('task.index'))

@task.route('/out_team',methods=['POST'])
@login_required
def out_team():
	oid = request.form['oid']
	order = Order.query.filter_by(id=oid).first()
	team_id = order.team_id
	Order.query.filter_by(id=oid).update({Order.team_id:None,Order.status_id:2,Order.update_man:current_user.id, \
		                                        Order.update_date:datetime.now()},synchronize_session=False)
	OrderProcess.save(oid,current_user.id,"订单踢出团队")
	db.session.commit()

	return jsonify({'result':True,'team_id':team_id})


@task.route('/to_group',methods=['POST'])
def to_group():
	oid = request.form['oid'];
	tid = request.form['tid'];

	group = OrderTeam.query.filter_by(id=tid).first()

	Order.query.filter_by(id=oid).update({Order.team_id:tid,Order.status_id:group.status_id, \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	
	OrderProcess.save(oid,current_user.id,u"订单加入 %s %s组 %s号机" %(group.name,group.section,group.no))
	return redirect(request.referrer)

@task.route('/complete_task',methods=['POST'])
@login_required
def complete_task():
	oids = request.form['oids']
	tid = request.form['tid']
	task = GroupTask.query.filter_by(id=tid).first()
	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()
	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,(u"完成任务 %s" %task.name))
		task = OrderTask.query.filter_by(order_id=oid).filter_by(task_id=tid).first()
		if task:
			pass
		else:
			OrderTask.save(oid,tid,current_user.id)
	order = Order.query.filter_by(id=oids.split(',')[0]).first()
	return jsonify({'result':True,'team_id':order.team_id})


@task.route('/over_task',methods=['POST'])
@login_required
def over_task():
	oids = request.form['oids']
	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.status_id:9,Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()
	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,"结束任务组")
	return redirect(request.referrer)

@task.route('/update_level',methods=['POST'])
@login_required
def update_level():
	oid = request.form['oid']
	now_level=request.form['now_level']
	Order.query.filter_by(id=oid).update({Order.now_level:now_level,Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	
	order = Order.query.filter_by(id=oid).first()
	OrderProcess.save(oid,current_user.id,u"更新等级至 %s" %now_level)
	return jsonify({'result':True,'team_id':order.team_id})


@task.route('/bug_order',methods=['POST'])
@login_required
def bug_order():
	oid = request.form['oid']
	issue_type = request.form['issue_type']
	issue_memo = request.form['issue_memo']
	Order.query.filter_by(id=oid).update({Order.is_issue:1,Order.issue_id:issue_type,Order.issue_memo:issue_memo, \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()

	OrderProcess.save(oid,current_user.id,u"标记为异常订单 异常信息为: %s" %issue_memo)
	order = Order.query.filter_by(id=oid).first()
	return jsonify({'result':True,'team_id':order.team_id})

@task.route('/unbug_order',methods=['POST'])
@login_required
def unbug_order():
	oid = request.form['oid']
	Order.query.filter_by(id=oid).update({Order.is_issue:0,Order.issue_id:None,Order.issue_memo:"", \
										  Order.update_date:datetime.now(),Order.update_man:current_user.id})
	db.session.commit()
	OrderProcess.save(oid,current_user.id,"解除异常")
	order = Order.query.filter_by(id=oid).first()
	return jsonify({'result':True,'team_id':order.team_id})

@task.route('/add_warning',methods=['POST'])
@login_required
def add_warning():
	oid = request.form['oid']
	warning_type = request.form['warning_type']
	content = request.form['content']

	Order.query.filter_by(id=oid).update({Order.warning_type:warning_type,Order.update_date:datetime.now(),Order.update_man:current_user.id},synchronize_session=False)
	db.session.commit()
	OrderWarning.save(oid,warning_type,content,current_user.id)
	
	order = Order.query.filter_by(id=oid).first()
	return jsonify({'result':True,'team_id':order.team_id})

@task.route('/_get_team/<tid>')
@login_required
def get_team(tid):
	team = OrderTeam.query.filter_by(id=tid).first()
	return jsonify(team.to_json())

@task.route('/_get_team_orders/<tid>')
@login_required
def get_team_orders(tid):
	orders = Order.query.filter_by(team_id=tid).all()
	tasks = GroupTask.query.filter_by(type=1).order_by('id').all()

	return render_template('task/orders.html',orders=orders,tasks=tasks)

@task.route('/__get_available_team/<type>')
@login_required
def get_available_team(type):
	status = [7,8]
	teams =  OrderTeam.query.filter_by(group_type=type).filter(OrderTeam.status_id.in_(status)).all()
	return render_template('team/teams.html',teams=teams)


@task.route('/export')
def export():
	tid = request.args.get('tid')
	orders = Order.query.filter_by(team_id=tid).all()
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
