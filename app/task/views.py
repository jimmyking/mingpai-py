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
	
	team = OrderGroup(group_type=1,name=name,no=no,status_id=7, \
		             create_man=current_user.id)
	db.session.add(team)
	db.session.commit()
	OrderGroupProcess.save(team.id,current_user.id,"创建任务分组")

	Order.query.filter(Order.id.in_(oids.split(','))).update({Order.group_id:team.id,Order.status_id:7, \
		                                                      Order.update_man:current_user.id, \
		                                                      Order.update_date:datetime.now()},synchronize_session=False)
	db.session.commit()
	for oid in oids.split(','):
		OrderProcess.save(oid,current_user.id,(u"分配到: %s组%s号机" %(name,no)))

	return redirect(url_for('order.orders'))