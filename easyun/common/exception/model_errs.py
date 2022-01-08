# -*- coding: utf-8 -*-
'''
    :file: model_errs.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2022/01/08 15:11:27
'''

class KeyPairsRepeat(Exception): 
    def __init__(self, err_msg:str = "key pair name was exit", *args: object) -> None:
        super().__init__(*args)
        self.err_msg = err_msg

    def __str__(self) -> str:
        return f'{self.err_msg}'