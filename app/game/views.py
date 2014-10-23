#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app
from flask import jsonify
from flask import request
from flask.ext.login import login_required
from ..models import Game,Area,Server
from .. import db
from . import game

#游戏管理
@game.route('/')
@login_required
def games():
	games = Game.query.order_by('id').all()
	return render_template('game/games.html',games=games)

@game.route('/add_game',methods=['POST'])
@login_required
def add_game():
	game = Game(name=request.form['name'])
	db.session.add(game)
	db.session.commit()
	return redirect(url_for('game.games'))

@game.route('/del_game',methods=['POST'])
@login_required
def del_game():
	gids = request.form['gids']
	Game.query.filter(Game.id.in_(gids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('game.games'))

@game.route('/update_game',methods=['POST'])
@login_required
def update_game():
	gid = request.form['id']
	name = request.form['name']
	Game.query.filter_by(id=gid).update({Game.name:name})
	db.session.commit()
	return redirect(url_for('game.games'))

@game.route('/_get_game/<gid>')
def get_game(gid):
	game = Game.query.filter_by(id=gid).first()
	return jsonify(game.to_json())


#区管理

@game.route('/areas/<gid>')
@login_required
def areas(gid):
	game = Game.query.filter_by(id=gid).first()
	areas = Area.query.filter_by(game_id=gid).all()
	return render_template('game/areas.html',game=game,areas=areas)

@game.route('/add_area',methods=['POST'])
@login_required
def add_area():
	gid = request.form['gid']
	area = Area(name=request.form['name'],game_id=gid)
	db.session.add(area)
	db.session.commit()
	return redirect(url_for('game.areas',gid=gid))

@game.route('/del_area',methods=['POST'])
@login_required
def del_area():
	gid = request.form['gid']
	aids = request.form['aids']
	Area.query.filter(Area.id.in_(aids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('game.areas',gid=gid))

@game.route('/update_area',methods=['POST'])
@login_required
def update_area():
	gid = request.form['gid']
	aid = request.form['id']
	name = request.form['name']
	Area.query.filter_by(id=aid).update({Area.name:name})
	db.session.commit()
	return redirect(url_for('game.areas',gid=gid))

@game.route('/_get_area/<aid>')
def get_area(aid):
	area = Area.query.filter_by(id=aid).first()
	return jsonify(area.to_json())



#服务器管理

@game.route('/servers/<gid>/<aid>')
@login_required
def servers(gid,aid):
	game = Game.query.filter_by(id=gid).first()
	area = Area.query.filter_by(id=aid).first()
	servers = Server.query.filter_by(area_id=aid).all()
	return render_template('game/servers.html',game=game,area=area,servers=servers)

@game.route('/add_server',methods=['POST'])
@login_required
def add_server():
	gid = request.form['gid']
	aid = request.form['aid']
	server = Server(name=request.form['name'],area_id=aid)
	db.session.add(server)
	db.session.commit()
	return redirect(url_for('game.servers',gid=gid,aid=aid))
	

@game.route('/del_server',methods=['POST'])
@login_required
def del_server():
	gid = request.form['gid']
	aid = request.form['aid']
	sids = request.form['sids']
	Server.query.filter(Server.id.in_(sids.split(','))).delete(synchronize_session=False)
	return redirect(url_for('game.servers',gid=gid,aid=aid))

@game.route('/update_server',methods=['POST'])
@login_required
def update_server():
	gid = request.form['gid']
	aid = request.form['aid']
	sid = request.form['id']
	name = request.form['name']
	Server.query.filter_by(id=sid).update({Server.name:name})
	db.session.commit()
	return redirect(url_for('game.servers',gid=gid,aid=aid))

@game.route('/_get_server/<sid>')
def get_server(sid):
	server = Server.query.filter_by(id=sid).first()
	return jsonify(server.to_json())



