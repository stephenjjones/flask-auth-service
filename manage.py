import os
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate
from flask_cors import CORS, cross_origin

from app import create_app, db
from app.models import User, Role



app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app) # flask_script
migrate = Migrate(app, db)
CORS(app)




def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)







if __name__ == '__main__':
    manager.run()
