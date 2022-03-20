# -*- coding: UTF-8 -*-
'''
@Description: Standardization for return.
@LastEditors: 
'''
from apiflask import Schema, abort
from apiflask.fields import String, Integer, Field, Nested
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES, http_date
from typing import Any, Union, Tuple


def generate_payload(
    detail: Any = None,
    message: str = "success",                     
    status_code: int = 200,
    task_id: str = None  
) -> dict:
    """生成格式化的响应体

    Args:
        detail (Any, optional): 响应的数据. Defaults to None.
        message (str, optional): 响应的消息. Defaults to "success".
        status_code (int, optional): 业务状态码. Defaults to 200.

    Returns:
        dict: 格式化好的载体
    """
    return {'detail': detail,'message': message, 'status_code': status_code, 'task_id': task_id}


def make_resp(
    detail: Any = None, 
    message: str = "success",
    status_code: int = 200,
    task_id: str = None,
    http_status_code: int = 200
) -> Tuple[dict, int]:
    """make a views function response

            The return value should match the base response schema
            and the data key should match

    Args:
        detail (Any, optional): 响应的数据. Defaults to None.
        message (str, optional): 响应的消息. Defaults to "success".
        status_code (int, optional): 业务状态码. Defaults to 200.
        task_id (str, optional): 异步任务ID. Defaults to None.
        http_status_code (int, optional): http状态码. Defaults to 200.

    Returns:
        Tuple[dict, int]: 格式化好的字典与http状态码
    """
    return generate_payload(detail=detail, message=message, status_code=status_code, task_id=task_id), http_status_code


def error_resp(status_code, message=None):
    abort(status_code=status_code, message=message)
    # payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    # if message:
    #     payload['message'] = message
    # response = jsonify(payload)
    # response.status_code = status_code
    # return response


def bad_request(message):
    return error_resp(400, message)


class Result:
    # 构造函数
    def __init__(self,
                 detail: Any = None,                  
                 message: str = "success", 
                 status_code: int = 200,
                 task_id: str = None,
                 http_status_code: int = 200                 
    ) -> None:
        """初始化响应数据类

        Args:
            detail (Any, optional): 响应的数据. Defaults to None.
            message (str, optional): 响应消息. Defaults to "success".
            status_code (int, optional): 业务状态码. Defaults to 200.
            task_id (str, optional): 异步任务ID. Defaults to None.
            http_status_code (int, optional): HTTP状态码. Defaults to 200.
        """
        self.detail = detail        
        self.message = message
        self.status_code = status_code
        self.task_id = task_id
        self.http_status_code = http_status_code

    def make_resp(self) -> Tuple[dict, int]:
        """构建success响应

            ```example
                @app.post("/")
                def login_test():
                    response = Result(detail=None, status_code=1001,
                                    message="ok", http_status_code=200)
                    return response.make_resp()

            ```
        Returns:
            Tuple[dict, int]: 响应体与http状态码
        """
        return make_resp(self.detail, self.message, self.status_code, self.task_id, self.http_status_code)

    def err_resp(self) -> None:
        """构建error响应

            ```example
                result = Result(detail=None, status_code=1001,
                            message="catch an error", http_status_code=500)
                result.err_resp()
            ```
        """
        if self.http_status_code == 200:
            self.http_status_code = 500
        abort(self.http_status_code,
              extra_data=generate_payload(
                  self.detail,
                  self.message,
                  self.status_code,
                  self.task_id
              ))
