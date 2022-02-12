# -*- coding: utf-8 -*-
'''
@Description: The Dashboard module
@LastEditors: 
'''
from apiflask import APIBlueprint, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


# define api version
ver = '/api/v1'

bp = APIBlueprint('监控面板', __name__, url_prefix = ver+'/dashboard') 

from . import api_inventory, api_summary, api_mock