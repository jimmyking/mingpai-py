#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required,current_user
from ..models import Order,Area,OrderProcess,OrderStatus,OrderGroup,OrderGroupProcess
from datetime import datetime
from .. import db
from . import team

@team.route('/')
@login_required
def index():
	pass

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
		OrderProcess.save(oid,current_user.id,u"分配到: %s%s%d组" %(name,area.name,no))

	return redirect(url_for('order.orders'))