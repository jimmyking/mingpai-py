from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.seesion_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)


    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .game import game as game_blueprint
    app.register_blueprint(game_blueprint, url_prefix='/game')

    from .dic import dic as dic_blueprint
    app.register_blueprint(dic_blueprint, url_prefix='/dic')

    from .order import order as order_blueprint
    app.register_blueprint(order_blueprint, url_prefix='/order')

    return app

