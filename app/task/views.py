#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from ..models import GroupTask,OrderTask,OrderGroupTask
from datetime import datetime
from .. import db
from . import task


@task.route('/')
@login_required
def index():
	teams =  OrderGroup.query.filter_by(group_type=1).filter(OrderGroup.status_id.in_([7,8])).all()
	tasks = GroupTask.query.filter_by(type=1).order_by('id').all()
	return render_template('task/index.html',teams=teams,tasks=tasks)

@task.route('/add_team',methods=['POST'])
@login_required
def add_team():
	oids = request.form['oids']
	name = request.form['name']
	no = request.form['no']
	target = request.form['target']
	team = OrderGroup(group_type=1,name=name,no=no,target=target,status_id=7, \
		             create_man=current_user.id)
	db.session.add(team)
	db.session.commit()
	OrderGroupProcess.save(team.id,current_user.id,"创建任务分组")

	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.group_id:team.id,Order.status_id:7, \
		                                                      Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()
	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,(u"分配到: %s  %s组%s号机" %(name,no,target)))

	return redirect(url_for('order.orders'))


@task.route('/start_task',methods=['POST'])
@login_required
def start_task():
	tid = request.form['tid']
	OrderGroup.query.filter_by(id=tid).update({OrderGroup.status_id:8,OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(tid,current_user.id,"开始任务")
	Order.query.filter_by(group_id=tid).update({Order.status_id:8, \
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
	OrderGroup.query.filter_by(id=tid).update({OrderGroup.status_id:9,OrderGroup.update_man:current_user.id, \
											   OrderGroup.update_date:datetime.now()},synchronize_session=False)
	OrderGroupProcess.save(tid,current_user.id,"任务完成")
	Order.query.filter_by(group_id=tid).update({Order.status_id:9, \
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


@task.route('/_get_team/<tid>')
@login_required
def get_team(tid):
	team = OrderGroup.query.filter_by(id=tid).first()
	return jsonify(team.to_task_json())

