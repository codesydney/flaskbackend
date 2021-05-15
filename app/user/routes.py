



from flask import request, current_app
from app import db
from app.user import bp
from app.auth.auth import token_auth
from app.models import User, Customer, Role
from app.errors.errors import error_response, bad_request
import re


def check_email_exist(email):
    if User.query.filter_by(email=email).first():
        return False
    return True

# create user - admin
@bp.route('users/admin', methods=['POST'])
def create_user():
    data = request.get_json() or {}

    mand_fields = ('email', 'password')
    if not all(field in data for field in mand_fields):
        return bad_request('Please provide all mandatory fields')
    if not check_email_exist(data['email']):
        return bad_request('email already registered')

    data['role_id'] = Role.query.filter_by(name='admin').first().id

    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()

    return user.to_dict()


# create user - customer
@bp.route('users/customer', methods=['POST'])
def create_customer():
    data = request.get_json() or {}

    mand_fields = ('email', 'password', 'first_name', 'last_name')
    if not all(field in data for field in mand_fields):
        return bad_request('Please provide all mandatory fields')
    if not check_email_exist(data['email']):
        return bad_request('email already registered')

    data['role_id'] = Role.query.filter_by(name='customer').first().id

    customer = Customer()
    customer.from_dict(data, new_user=True)
    db.session.add(customer)
    db.session.commit()

    return customer.to_dict()


# update customer
# Note that id is the user id not customer id
@bp.route('users/customer/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_customer(id):
    customer = User.query.filter_by(id=id).first().customer
    if not customer:
        error_response(404,'Customer does not exist')
     
    data = request.get_json() or {}
    if data:
        customer.from_dict(
            data, update_by=token_auth.current_user().email)
        db.session.commit()

    return customer.to_dict()


# get all customers
@bp.route('users/customer', methods=['GET'])
def get_all_customers():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get(
        'per_page', current_app.config['PAGINATION_MIN'], type=int),
        current_app.config['PAGINATION_MAX'])
    data = Customer.to_collection_dict(
        Customer.query, page, per_page, 'user.get_all_customers')
    return data


# get one customer
# note id is user id not customer id
@bp.route('users/customer/<int:id>', methods=['GET'])
def get_customer(id):
    customer = User.query.filter_by(id=id).first().customer
    if not customer:
        return error_response(404,'Customer does not exist')
    return customer.to_dict()
