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

    from .team import team as team_blueprint
    app.register_blueprint(team_blueprint, url_prefix='/team')

    from .task import task as task_blueprint
    app.register_blueprint(task_blueprint, url_prefix='/task')

    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint, url_prefix='/search')

    from .warning import warning as warning_blueprint
    app.register_blueprint(warning_blueprint, url_prefix='/warning')

    return app

