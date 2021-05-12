from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.errors.errors import error_response
from app.models import User


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


# this funcion receives the username, password sent by client
# If valid it will return a user object.
# You can then access the user object via current_user()
@basic_auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user


# this function is called if there is an error with basic authentication
@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status, 'You have entered incorrect login credentials')


# used by http-auth to provide authentication based on roles
@basic_auth.get_user_roles
@token_auth.get_user_roles
def get_user_roles(user):
    return [user.role.name]


# this funcion receives the token sent by Quasar
# If valid it will return a user object
# You can then access the user object via current_user()
@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


# this function is called if there is an error with token authentication
@token_auth.error_handler
def auth_error(status):
    if status == 401:
        return error_response(status, 'Your login token is invalid')
    elif status == 403:
        return error_response(status, "You don't have permission to access this page")
    else:
        return error_response(status, "Token error")


# used by http-auth to provide authentication based on roles
@basic_auth.get_user_roles
@token_auth.get_user_roles
def get_user_roles(user):
    return [user.role.name]