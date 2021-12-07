# -*- coding: utf-8 -*-
"""The Dashboard module."""
from apiflask import APIBlueprint, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

# define api version
ver = '/api/v1.0'

bp = APIBlueprint('监控面板', __name__, url_prefix = ver) 

