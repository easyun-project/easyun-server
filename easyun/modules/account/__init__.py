# -*- coding: utf-8 -*-
"""The Account management module."""
from apiflask import APIBlueprint, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

# define api version
ver = '/api/v1/account'

bp = APIBlueprint('账号管理', __name__, url_prefix = ver) 

from . import view