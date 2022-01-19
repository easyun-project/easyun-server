# -*- coding: utf-8 -*-
'''
    :file: view.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2022/01/20 01:33:42
'''


import typing as t

from werkzeug.routing import BaseConverter

class PhoneConverter(BaseConverter):
    """匹配中国手机号码"""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.regex = "13[0-9]{9}"

