# -*- coding: utf-8 -*-
'''
    :file: view.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2022/01/20 01:43:11
'''

from . import bp

@bp.get("/phone/<phone:phone>")
def get_info(phone):
    print(f"user phone: {phone}")
    return f"用户手机号: {phone}"
