#!/usr/bin/env python
# encoding: utf-8
"""
  @author:  shui
  @file:    celery.py
  @time:    2022/1/3 20:52
  @desc:
"""
from celery import Celery

class FlaskCelery(Celery):

    def init_app(self, app):
        # 加载app配置
        self.conf.update(app.config)

        class ContextTask(self.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        # 加载flask上下文
        self.Task = ContextTask
