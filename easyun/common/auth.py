# -*- coding: UTF-8 -*-
'''
@Description: The user auth module.
@LastEditors:
'''

from apiflask import (
    APIBlueprint,
    HTTPTokenAuth,
    HTTPBasicAuth,
    abort,
    auth_required,
    doc,
)
from .result import Result
from .models import User, Account
from .schemas import LoginParm, UsernameParm, UserModel, PasswordParm, AddUserParm
from .. import db

# define api version
ver = '/api/v1'

bp = APIBlueprint('用户认证', __name__, url_prefix=ver + '/user')

auth_basic = HTTPBasicAuth()
auth_token = HTTPTokenAuth(scheme='Bearer')


@auth_basic.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        return user


@auth_basic.error_handler
def basic_auth_error(status):
    result = Result(http_status_code=status)
    return result.err_resp()


@auth_token.verify_token
def verify_token(token):
    user: User = User.check_token(token) if token else abort(401)
    if user:
        return user
    abort(401)


@auth_token.error_handler
def token_auth_error(status):
    result = Result(http_status_code=status)
    return result.err_resp()


@bp.post('/auth')
@bp.input(LoginParm)
@bp.output(UserModel)
def login_user(user):
    '''用户登录 (auth token)'''
    # if 'username' not in user or 'password' not in user:
    #     return bad_request('must include username and password fields')
    userName = user["username"]
    userPasswd = user['password']
    try:
        thisUser = User.query.filter_by(username=userName).first()
        if thisUser and thisUser.verify_password(userPasswd):
            # token = auth_token.current_user.get_token()
            authToken = thisUser.get_token()
            db.session.commit()
            # get account info from database
            cloudAccount: Account = Account.query.first()
            resp = Result(
                detail={
                    'token': authToken,
                    'account_id': cloudAccount.account_id,
                    'account_type': cloudAccount.aws_type,
                    'role': cloudAccount.role,
                    'deploy_region': cloudAccount.get_region(),
                },
                status_code=200,
            )
            return resp.make_resp()
        else:
            raise ValueError('Username and Password do not match.')
    except Exception as ex:
        response = Result(message=str(ex), status_code=1004, http_status_code=400)
        response.err_resp()


@bp.delete('/logout')
@auth_required(auth_token)
def logout_user():
    '''注销当前用户 (revoke token)'''
    # Headers
    # Token Bearer Authorization
    auth_token.current_user.revoke_token()
    db.session.commit()
    resp = Result(detail={'status': 'Current user logout.'}, status_code=200)
    return resp.make_resp()


@bp.put('/password')
@auth_required(auth_token)
@bp.input(PasswordParm)
def change_passowrd(parm):
    '''修改当前用户密码'''
    auth_token.current_user.set_password(parm['password'])
    db.session.commit()
    resp = Result(detail={'status': 'Password changed.'}, status_code=200)
    return resp.make_resp()


@bp.post('')
@auth_required(auth_token)
@bp.input(AddUserParm)
@bp.output(UserModel)
@doc(tag='【仅限测试用】', operation_id='Add New User')
def add_user(parm):
    '''添加新用户'''
    try:
        if 'username' not in parm or 'password' not in parm:
            result = Result(
                http_status_code=400, message='must include username and password fields'
            )
            return result.err_resp()
        if User.query.filter_by(username=parm['username']).first():
            result = Result(http_status_code=400, message='please use a different username')
            return result.err_resp()
        if User.query.filter_by(email=parm['email']).first():
            result = Result(
                http_status_code=400, message='please use a different email address'
            )
            return result.err_resp()

        newUser = User()
        newUser.from_dict(parm, new_user=True)
        # user.from_dict(newuser, new_user=True)
        db.session.add(newUser)
        db.session.commit()

        resp = Result(detail=newUser, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=1001, http_status_code=400)
        response.err_resp()


@bp.delete('')
@auth_required(auth_token)
@bp.input(UsernameParm)
@doc(tag='【仅限测试用】', operation_id='Delete a User')
def delete_user(parm):
    '''删除指定用户'''
    try:
        uname = parm['username']
        delUser = User.query.filter_by(username=uname).first()
        if delUser:
            db.session.delete(delUser)
            db.session.commit()
        else:
            raise ValueError(f'[User] {uname} does not exist.')
        resp = Result(
            message=f'[User] {delUser.username} delete successfully !',
            status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=1002, http_status_code=400)
        response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.output(UserModel(many=True))
@doc(tag='【仅限测试用】', operation_id='List all Users')
def list_user():
    '''查询当前用户列表'''
    try:
        users = User.query.order_by(User.id)
        resp = Result(detail=users, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=1003, http_status_code=400)
        response.err_resp()


# @bp.get('/token')
# @auth_required(auth_basic)
# @doc(tag='【仅限测试用】', operation_id='Get token')
# def get_auth_token():
#     '''基于auth_basic, Get方法获取token'''
#     token = auth_basic.current_user.get_token()
#     db.session.commit()
#     result = Result(detail={'token': token})
#     return result.make_resp()
