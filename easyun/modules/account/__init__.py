# -*- coding: utf-8 -*-
"""The Account management module."""

from apiflask import APIBlueprint

# define api version
ver = '/api/v1'

bp = APIBlueprint('账号管理', __name__, url_prefix=ver + '/account')

from . import api_qouta, api_keypair
