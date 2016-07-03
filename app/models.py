from flask import current_app, g
from marshmallow import Schema, fields, validate
from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from . import db, auth


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
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
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

