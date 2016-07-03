from flask import request, abort, jsonify, g, url_for
from . import main
from .. import db, auth
from ..models import User


@main.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Your browser is %s</h1>' % user_agent

@main.route('/api/users', methods = ['POST'])
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

@main.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'email': user.email})

@main.route('/api/token', methods = ['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


