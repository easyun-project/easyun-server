# -*- coding: utf-8 -*-
'''
    :file: __init__.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2022/01/20 01:32:21
'''
from apiflask import APIBlueprint

ver = '/api/v1'

bp = APIBlueprint('Demo', __name__, url_prefix=ver + '/demo')

from . import view