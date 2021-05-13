



from flask import request, current_app
from app import db
from app.main import bp
from app.auth.auth import token_auth
from app.models import User, Customer, Role, Job, JobStatus
from app.errors.errors import error_response


# create customer
@bp.route('users/customer', methods=['POST'])
@token_auth.login_required
def create_customer():
    data = request.body_params.dict()
    data['role_id'] = Role.query.filter_by(name='customer').first().id

    customer = Customer()
    customer.from_dict(
        data, update_by=token_auth.current_user().email, new_user=True)
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
     
    data = request.body_params.dict()
    customer.from_dict(
        data, update_by=token_auth.current_user().email)
    db.session.commit()

    return customer.to_dict()


# create job
@bp.route('job', methods=['POST'])
@token_auth.login_required
def create_job():
    data = request.get_json() or {}
    data = map_userid(data)

    job = Job()
    job.from_dict(data, update_by=token_auth.current_user().email)
    db.session.add(job)
    db.session.commit()
    
    return job.to_dict()


# update job
@bp.route('job/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_job(id):
    job = Job.query.get_or_404(id)
    data = request.get_json() or {}
    data = map_userid(data)

    job.from_dict(data, update_by=token_auth.current_user().email)
    db.session.add(job)
    db.session.commit()

    return job.to_dict()


# delete job
@bp.route('job/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_job(id):
    job = Job.query.get_or_404(id)
    if job.tradesperson.id != token_auth.current_user().tradesperson.id:
        return error_response(403, 'You are not authorised.')
    db.session.delete(job)
    db.session.commit()

    return {'message': 'job deleted'}


# get one job
@bp.route('job/<int:id>', methods=['GET'])
@token_auth.login_required
def get_job(id):
    job = Job.query.get_or_404(id)
    
    return job.to_dict()


# get all jobs under tradesperson
@bp.route('job', methods=['GET'])
@token_auth.login_required
def get_all_job():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get(
        'per_page', current_app.config['PAGINATION_MIN'], type=int),
        current_app.config['PAGINATION_MAX'])
    curr_user = token_auth.current_user()
    query = Job.query.filter_by(tradesperson=curr_user.tradesperson)
    data = Job.to_collection_dict(
        query, page, per_page, 'api_v1.get_all_job')
    
    return data


# get all job status
@bp.route('job_status', methods=['GET'])
def get_all_job_status():
    job_status = JobStatus.query
    data = JobStatus.to_collection_dict(
        JobStatus.query, 1, 100, 'api_v1.get_all_job_status')
    
    return data

