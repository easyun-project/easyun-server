# -*- coding: UTF-8 -*-
'''
@Description: Standardization for return.
@LastEditors: 
'''
from apiflask import abort
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

class Result:
    """
        >>> result = Result()
        >>> result.make_resp()
        {
            'detail': None,
            'message': "success",
            'status_code': 200,
            'task_id': ""
        }, 200
    """
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
        return generate_payload(detail=self.detail, message=self.message,
                                status_code=self.status_code,
                                task_id=self.task_id), self.http_status_code

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
