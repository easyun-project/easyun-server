#!/usr/bin/env python
# encoding: utf-8
"""
  @author:  shui
  @file:    config.py
  @time:    2021/12/29 21:29
  @desc:
"""

class BaseConfig:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'