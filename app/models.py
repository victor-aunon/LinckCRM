from app import db, login
from datetime import datetime, timedelta
from time import time
import jwt
import json
import base64
import os
import enum
from flask import current_app, url_for
from flask_login import UserMixin
from flask_babel import _
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class PermissionsEnum(enum.Enum):
    owner = 'Owner'
    admin = 'Admin'
    user = 'User'


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    company_id = db.Column(db.String(64),
                           db.ForeignKey('my_company.id'))
    tutorials = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.Enum(PermissionsEnum),
                            default=PermissionsEnum.user)

    # Messages user implementation
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    # notifications = db.relationship('Notification', backref='user',
    #                                 lazy='dynamic')

    # API token implementation
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_company(self, company_id):
        self.company_id = company_id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() +
                           expires_in},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod  # It can be invoked directly from the class
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    # def add_notification(self, name, data):
    #     # If a notification with the same name already exists
    #     # it is removed first
    #     self.notifications.filter_by(name=name).delete()
    #     n = Notification(name=name, payload_json=json.dumps(data), user=self)
    #     db.session.add(n)
    #     return n

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Message {}>'.format(self.body)


# class Notification(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     timestamp = db.Column(db.Float, index=True, default=time)
#     payload_json = db.Column(db.Text)

#     def get_data(self):
#         return json.loads(str(self.payload_json))


class MyCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    address = db.Column(db.String(150))
    postal_code = db.Column(db.Integer)
    city = db.Column(db.String(64))
    province = db.Column(db.String(64))
    phone1 = db.Column(db.String(64), index=True)
    phone2 = db.Column(db.String(64), default='')
    fax = db.Column(db.String(64), index=True, default='')
    cif = db.Column(db.String(64), index=True, unique=True)
    iva = db.Column(db.Float)
    IBAN = db.Column(db.String(64))
    users = db.relationship('User', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<MyCompany {}>'.format(self.name)

    # Email implementation
    emails_sent = db.relationship('Email', foreign_keys='Email.recipient_id',
                                  backref='author', lazy='dynamic')


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.Integer, index=True, unique=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    address = db.Column(db.String(150))
    postal_code = db.Column(db.Integer)
    city = db.Column(db.String(64))
    province = db.Column(db.String(64))
    phone1 = db.Column(db.String(64), index=True)
    phone2 = db.Column(db.String(64), default='')
    fax = db.Column(db.String(64), index=True, default='')
    client_since = db.Column(db.DateTime, default=datetime.today)
    cif = db.Column(db.String(64), index=True, unique=True)
    IBAN = db.Column(db.String(64))
    invoices = db.relationship('Invoice', backref='author', lazy='dynamic')
    products = db.Column(db.PickleType)

    def __repr__(self):
        return '<Company {} ID:{}>'.format(self.name, self.ID)


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Email {}>'.format(self.body)

# class Invoice(db.Model):
#     def get_starting_date(self):
#         return datetime.today().replace(month=datetime.today().month -
#                                         1).replace(day=1)

#     def get_ending_date(self):
#         return datetime.today().replace(day=1) - timedelta(days=1)

#     id = db.Column(db.Integer, primary_key=True)
#     ID = db.Column(db.Integer, index=True, unique=True)
#     company = db.Column(db.Integer, db.ForeignKey('company.ID'))
#     base = db.Column(db.Float)
#     expense = db.Column(db.Float)
#     tax = db.Column(db.Float)
#     discount = db.Column(db.Float)
#     total = db.Column(db.Float)
#     date = db.Column(db.DateTime, index=True, default=datetime.today)
#     expiration = db.Column(db.DateTime, default=datetime.today)
#     starting_date = db.Column(db.DateTime, default=get_starting_date)
#     ending_date = db.Column(db.DateTime, default=get_ending_date)
#     payment_method = db.Column(db.String(140))

#     def __repr__(self):
#         return '<Invoice {} Company:{} Total:{}>'.format(self.ID, self.company,
#                                                          self.total)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
