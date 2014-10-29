#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from ..models import GroupTask,OrderTask,OrderGroupTask
from datetime import datetime
from .. import db
from . import team

@team.route('/')
@login_required
def index():
	teams =  OrderGroup.query.filter_by(group_type=0).filter(OrderGroup.status_id.in_([3,4])).all()
	tasks = GroupTask.query.filter_by(type=0).order_by('id').all()
	return render_template('team/index.html',teams=teams,tasks=tasks)

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

	return redirect(url_for('order.orders'))

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