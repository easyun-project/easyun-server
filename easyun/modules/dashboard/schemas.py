# encoding: utf-8
"""
  @module:  Dashboard Schema
  @desc:    Dashboard Input/output schema
  @author:  aleck
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf

