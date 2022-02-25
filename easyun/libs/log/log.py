#!/usr/bin/env python
# encoding: utf-8
"""
  @file:    log.py
  @desc:
  @time:    2022/1/22 21:42
  @author:  shui
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler
from functools import wraps


Main_API_Log = 'logs/easyun_api.log'
Formatter = '%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
Level_Dict = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

class EasyunLogging:
    """
    易云公共日志模块, 支持flask初始化
    """
    def __init__(self, app_name='easyun', formatter=Formatter):
        """初始化"""
        self.app_name = app_name
        self.formatter = logging.Formatter(formatter)

    def init_app(self, app, level='info'):
        """初始化应用的根logger"""
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(Main_API_Log, maxBytes=10240, backupCount=10)
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(Level_Dict[level])

        root = logging.getLogger()
        root.addHandler(file_handler)
        root.exception('Probably something went wrong', extra={'stack': True})

        app.logger.addHandler(default_handler)
        app.logger.addHandler(file_handler)

    def create_logger(self, module_name="default", level='info', console=True, file=True):
        """创建logger"""
        # log_name = f"{self.app_name}.{module_name}"
        log_name = f"{module_name}"
        file_name = f"logs/{self.app_name}_{module_name}.log"

        logger = logging.getLogger(log_name)
        logger.setLevel(Level_Dict[level])

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            logger.addHandler(console_handler)

        if file:
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(self.formatter)
            logger.addHandler(file_handler)

        return logger


    def api_logger(self, logger, level='error'):
        """记录api的进出口日志的装饰器, 默认error级别"""
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.exception(e)
                    raise e
            return wrapper
        return decorate
