#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Order, OrderStatus, OrderGroup
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import current_user


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)



@app.context_processor
def inject_user():
    return dict(user=current_user)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Order=Order, OrderStatus=OrderStatus,\
                OrderGroup=OrderGroup)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)





if __name__ == '__main__':
    manager.run()
