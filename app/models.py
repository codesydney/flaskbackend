from flask import current_app, url_for
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import jwt


# Generic pagination mixin if you want to perform pagination via backend
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


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    job = db.relationship(
        "Job", backref="customer", lazy="dynamic")
    update_by = db.Column(db.String(30), nullable=False)
    update_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    create_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.user.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'address': self.address,
            'last_login': self.user.last_login.isoformat() + 'Z' if self.user.last_login else None,
            'current': self.user.current,
            'role': self.user.role.to_dict(),
        }
        return data

    def from_dict(self, data, update_by='sys user', new_user=False):
        if new_user:
            user = User(email=data['email'].lower())
            user.set_password(data['password'])
            user.role_id = data['role_id']
            self.user = user
        else:
            if 'password' in data and data['password'] is not None:
                self.user.set_password(data['password'])
        for key in data:
            if data[key] is not None and key not in ['email', 'password', 'role_id']:
                setattr(self, key, data[key])
        self.user.update_by = update_by
        self.user.update_date = datetime.utcnow()
        self.update_by = update_by
        self.update_date = datetime.utcnow()

    def __repr__(self):
        return '<Customer {}>'.format(self.name)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(140), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    customer = db.relationship(
        "Customer", uselist=False, foreign_keys=[Customer.user_id],
        backref="user", passive_deletes=True)
    last_login = db.Column(db.DateTime)
    current = db.Column(db.Boolean, default=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(
        'role.id'), nullable=False)
    update_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    create_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'last_login': self.last_login.isoformat() + 'Z' if self.last_login else None,
            'current': self.current,
            'role': self.role.to_dict()
        }
        return data

    def from_dict(self, data, update_by='sys_user'):
        for key in data:
            if data[key] is not None and key not in ['email', 'password']:
                if hasattr(self, key):
                    setattr(self, key, data[key])
        if 'email' in data and data['email'] is not None:
            self.email = data['email'].lower()
        if 'password' in data and data['password'] is not None:
            self.set_password(data['password'])
        self.update_by = update_by
        self.update_date = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # If token hasn't expired yet then return existing token
    # Otherwise create a new token with expiry date 60 minutes from now
    # Update database with token info and return token
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        payload = {'user': self.id, 'exp': now + timedelta(seconds=expires_in)}
        self.token = jwt.encode(
            payload, current_app.config['SECRET_KEY'],
            algorithm='HS256')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.add(self)

    @ staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    @ staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return None
        return User.query.get(id)

    def get_temp_token(self, expires_in):
        return jwt.encode({'reset_password': self.id,
                           'exp': datetime.utcnow() +
                           timedelta(seconds=expires_in)},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256')

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')
    update_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class JobStatus(PaginatedAPIMixin, db.Model):
    __tablename__='job_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    job = db.relationship(
        "Job", backref="job_status", lazy="dynamic")
    update_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

    def __repr__(self):
        return '<JobStatus {}>'.format(self.name)


class Job(PaginatedAPIMixin, db.Model):
    __tablename__='job'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    job_status_id = db.Column(db.Integer, db.ForeignKey(
        'job_status.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    update_by = db.Column(db.String(30), nullable=False)
    update_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    create_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'job_status': self.job_status.to_dict(),
            'customer': self.customer.to_dict(),
            'inventory_id': [i.to_dict() for i in self.inventory.all()]
        }
        return data

    def from_dict(self, data, update_by='sys user'):
        for key in data:
            if data[key] is not None and key not in ['inventory_id']:
                if hasattr(self, key):
                    setattr(self, key, data[key])

        inventory = []
        if 'inventory_id' in data and data['inventory_id'] is not None:
            for iid in data['inventory_id']:
                inventory.append(Inventory.query.filter_by(id=int(iid)).first())
        if len(inventory) > 0:
            self.inventory = []
            for i in inventory:
                self.inventory.append(i)

        self.update_by = update_by
        self.update_date = datetime.utcnow()

    def __repr__(self):
        return '<Job {}>'.format(self.name)