#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from ..models import GroupTask,OrderTask,OrderTeam
from datetime import datetime
from .. import db
from . import task


@task.route('/')
@login_required
def index():
	teams =  OrderTeam.query.filter(OrderTeam.status_id.in_([7,8])).all()
	orders = Order.query.filter_by(status_id=6).order_by('id desc').all()
	tasks = GroupTask.query.filter_by(type=1).order_by('id desc').all()

	return render_template('task/index.html',teams=teams,orders=orders,tasks=tasks)

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
	Order.query.filter_by(id=oid).update({Order.team_id:None,Order.status_id:2,Order.update_man:current_user.id, \
		                                        Order.update_date:datetime.now()},synchronize_session=False)
	OrderProcess.save(oid,current_user.id,"订单踢出团队")
	db.session.commit()
	return redirect(url_for('task.index'))


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
	return redirect(request.referrer)


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
	
	OrderProcess.save(oid,current_user.id,u"更新等级至 %s" %now_level)
	return redirect(request.referrer)


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

