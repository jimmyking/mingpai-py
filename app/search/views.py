#encoding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request,Response
from flask.ext.login import login_required,current_user
from . import search
from datetime import date
from ..models import OrderType,IssueType,Area,OrderStatus,Order
from .. import db
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers

@search.route('/')
@login_required
def index():
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

    wangwang = request.args.get('wangwang')
    if wangwang:
        order_query = order_query.filter_by(wangwang=wangwang)
    mobile = request.args.get('mobile')
    if mobile:
        order_query = order_query.filter_by(mobile=mobile)


    orders = list()
    if order_no or acter_name or wangwang or mobile:
        orders = order_query.order_by('id desc').all()


    return render_template('search/index.html',ordertypes=ordertypes,issuetypes=issuetypes,orders=orders,areas=areas,status=status)

@search.route('/export')
def export():
    order_query = Order.query.filter_by(is_delete=0)
    order_no = request.args.get('order_no')
    if order_no:
        order_query = order_query.filter_by(order_no=order_no)
    acter_name = request.args.get('acter_name')
    if acter_name:
        order_query = order_query.filter_by(acter_name=acter_name)
   
    wangwang = request.args.get('wangwang')
    if wangwang:
        order_query = order_query.filter_by(wangwang=wangwang)
    mobile = request.args.get('mobile')
    if mobile:
        order_query = order_query.filter_by(mobile=mobile)


    orders = order_query.order_by('id desc').all()
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


