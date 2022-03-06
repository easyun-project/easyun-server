# -*- coding: UTF-8 -*-
'''
@Description: The user auth module.
@LastEditors: 
'''

from apiflask import APIBlueprint, HTTPTokenAuth, HTTPBasicAuth, auth_required, Schema, doc
from apiflask.validators import Length, OneOf, Email
from apiflask.fields import String, Integer, DateTime
from .result import Result, make_resp, error_resp, bad_request
from .models import User, Account
from .. import db

# define api version
ver = '/api/v1'

bp = APIBlueprint('用户认证', __name__, url_prefix = ver+'/user') 

auth_basic = HTTPBasicAuth()
auth_token = HTTPTokenAuth(scheme='Bearer')


@auth_basic.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        return user

@auth_basic.error_handler
def basic_auth_error(status):
    return error_resp(status)

@auth_token.verify_token
def verify_token(token):
    return User.check_token(token) if token else None
    if token in tokens:
        return tokens[token]

@auth_token.error_handler
def token_auth_error(status):
    return error_resp(status)


class UserDetail(Schema):
    id = Integer()
    username = String()
    email = String()
    token = String()
    token_expiration = DateTime()
    #cloud account info
    account_id = String()
    account_type = String()
    role = String()
    deploy_region = String()


class UserBrief(Schema):
    id = Integer()
    username = String()
    email = String()


class AddUserParm(Schema):
    username = String(
        required=True, validate=Length(0, 20), 
        example="user")
    password = String(
        required=True, validate=Length(0, 30), 
        example="password")
    email = String(
        required=True, validate=Email(), 
        example="user@mail.com")


class NewPassword(Schema):
    password = String(
        required=True, validate=Length(0, 20),
        example="Passw0rd")


class UserLogin(Schema):
    username = String(
        required=True, validate=Length(0, 20), 
        example='demo')
    password = String(
        required=True, validate=Length(0, 30),
        example='easyun')



@bp.post('/auth')
@bp.input(UserLogin)
@bp.output(UserDetail)
def login_user(user):
    '''用户登录 (auth token)'''
    # if 'username' not in user or 'password' not in user:
    #     return bad_request('must include username and password fields')
    userName = user["username"]
    userPasswd = user['password']
    thisUser = User.query.filter_by(username=userName).first()
    if thisUser and thisUser.verify_password(userPasswd):
        # token = auth_token.current_user.get_token()
        authToken = thisUser.get_token()
        db.session.commit()
        # get account info from database
        cloudAccount:Account = Account.query.first()
        resp = Result(
            detail = {
                'token': authToken,
                'account_id': cloudAccount.account_id,
                'account_type': cloudAccount.aws_type,
                'role': cloudAccount.role,
                'deploy_region': cloudAccount.get_region()
            }, 
            status_code=200)    
        return resp.make_resp()
        # jsonify({'token': token})
    else:
        return error_resp(401)


@bp.delete('/logout')
@auth_required(auth_token)
def logout_user():
    '''注销当前用户 (revoke token)'''
    # Headers
    # Token Bearer Authorization
    auth_token.current_user.revoke_token()
    db.session.commit()
    resp = Result(
        detail={'status': 'Current user logout.' },
        status_code=200)    
    return resp.make_resp()


@bp.put('/password')
@auth_required(auth_token)
@bp.input(NewPassword)
def change_passowrd(parm):
    '''修改当前用户密码'''
    auth_token.current_user.set_password(parm['password'])
    db.session.commit()
    resp = Result(
        detail={'status': 'Password changed.' }, 
        status_code=200)    
    return resp.make_resp()


# @bp.post('/adduser')
# @auth_required(auth_token)
@bp.input(AddUserParm)
@bp.output(UserDetail)
@doc(tag='【仅限测试用】', operation_id='Add New User')
def add_user(parm):
    '''向数据库添加新用户'''
    if 'username' not in parm or 'password' not in parm:
        return bad_request('must include username and password fields')
    if User.query.filter_by(username=parm['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=parm['email']).first():
        return bad_request('please use a different email address')

    newUser = User()
    newUser.from_dict(parm, new_user=True)
    # user.from_dict(newuser, new_user=True)
    db.session.add(newUser)
    db.session.commit()

    resp = Result(
        detail = newUser,
        status_code=200)
    return resp.make_resp()


@bp.get('/token')
@auth_required(auth_basic)
@doc(tag='【仅限测试用】', operation_id='Get token')
def get_auth_token():
    '''基于auth_basic, Get方法获取token'''
    token = auth_basic.current_user.get_token()
    db.session.commit()
    # return jsonify({'token': token})
    return make_resp('Success', 200, {'token': token})
