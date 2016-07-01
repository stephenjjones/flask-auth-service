from flask import Flask, request, abort, jsonify, g, url_for
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_migrate import MigrateCommand, Migrate
from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

#from flask_wtf import Form
#from wtforms import StringField, PasswordField, validators
from marshmallow import Schema, fields, validate


app = Flask(__name__)

# Move this to an environment variable
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://authuser:secretpassword@localhost:5432/authsvc'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))


user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User',
        secondary=user_roles,
        backref=db.backref('roles', lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),
        nullable=False)
    is_active = db.Column(db.Boolean, server_default="false", nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.email

    def hash_password(self, password):
        ph = PasswordHasher()
        self.password_hash = ph.hash(password)

    def verify_password(self, password):
        ph = PasswordHasher()
        return ph.verify(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


class UserSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer(dump_only=True)
    email = fields.Email(validate=not_blank)
    password = fields.String(validate=not_blank)
    is_active = fields.Boolean()

    class Meta:
        type_ = 'users'


@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with email/password
        user = User.query.filter_by(email = email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True



@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Your browser is %s</h1>' % user_agent

@app.route('/api/users', methods = ['POST'])
def new_user():
    schema = UserSchema()
    result = schema.load(request.get_json())
    if request.method != 'POST' or not result:
        abort(400)
    email = result.data['email']
    password = result.data['password']
    if User.query.filter_by(email = email).first() is not None:
        abort(400)
    user = User(email = email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({ 'email': user.email }), 201,
        {'Location': url_for('get_user', id = user.id, _external = True)})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'email': user.email})

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


if __name__ == '__main__':
    manager.run()
