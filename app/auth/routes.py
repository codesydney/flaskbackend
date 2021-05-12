from flask import jsonify, request, current_app
from app.auth import bp
from app import db
from app.auth.auth import basic_auth, token_auth
from app.models import User
from app.errors.errors import error_response,  bad_request
from app.email.email import send_forgotpwd_email
from datetime import datetime


# basic auth or token auth is passed so user is now logged in
# return either a new token or an existing token back to Vue
# This is the route Vue calls when user first login
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    data = request.get_json() or {}
    remember_me = data.get('remember_me')
    expiry = 3600 # default 1 hour token expiry
    if remember_me:
        expiry = 604800 # 7 days token expiry
    token = user.get_token(expires_in = expiry)
    payload = {
        'token': token,
        'email': user.email,
        'user_id': user.id,
        'role' : user.role.name,
    }
    user.last_login = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return payload


# revoke a token immediately .. eg when user logs out
@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    # 204 - successful and no body
    return '', 204


@bp.route('/forgot_password/<email>', methods=['POST'])
def forgot_password(email):
    user = User.query.filter_by(email=email).first()
    if user:
        if send_forgotpwd_email(user):
            return '', 204
        else:
            return error_response(502, 'unable to send email')
    else:
        return error_response(400, "email doesn't exist")


@bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    user = User.verify_temp_token(token)
    if not user:
        return error_response(401, 'token is not valid')
    data = request.body_params.dict()
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return '', 204


# testing
@bp.route('/hello', methods=['GET'])
def hello():
    return {'message': 'hello world!'}