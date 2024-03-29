# -*- coding: UTF-8 -*-
'''
@Description: Standardization for return.
@LastEditors: 
'''
from apiflask import abort
from typing import Any, Union, Tuple

# def error_resp(status_code, message=None):
#     abort(status_code=status_code, message=message)

# def bad_request(message):
#     return error_resp(400, message)


def generate_payload(
    detail: Any = None,
    message: str = "success",
    status_code: int = 200,
    task: Any = None,
) -> dict:
    """生成格式化的响应体

    Args:
        detail (Any, optional): 响应的数据. Defaults to None.
        message (str, optional): 响应的消息. Defaults to "success".
        status_code (int, optional): 业务状态码. Defaults to 200.

    Returns:
        dict: 格式化好的载体
    """
    return {
        'detail': detail,
        'message': message,
        'status_code': status_code,
        'task': task,
    }


class Result:
    """
    >>> result = Result()
    >>> result.make_resp()
    {
        'detail': None,
        'message': "success",
        'status_code': 200,
        'task': None
    }, 200
    """

    # 构造函数
    def __init__(
        self,
        detail: Any = None,
        message: str = "success",
        status_code: int = 200,
        task: Any = None,
        http_status_code: int = 200,
    ) -> None:
        """初始化响应数据类

        Args:
            detail (Any, optional): 响应的数据. Defaults to None.
            message (str, optional): 响应消息. Defaults to "success".
            status_code (int, optional): 业务状态码. Defaults to 200.
            task (Any, optional): 异步任务信息. Defaults to None.
            http_status_code (int, optional): HTTP状态码. Defaults to 200.
        """
        self.detail = detail
        self.message = message
        self.status_code = status_code
        self.task = task
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
        return (
            generate_payload(
                detail=self.detail,
                message=self.message,
                status_code=self.status_code,
                task=self.task,
            ),
            self.http_status_code,
        )

    def err_resp(self) -> None:
        """构建error响应

        ```example
            result = Result(detail=None, status_code=1001,
                        message="catch an error", http_status_code=400)
            result.err_resp()
        ```
        """
        if self.http_status_code == 200:
            self.http_status_code = 400
        abort(
            self.http_status_code,
            extra_data=generate_payload(
                self.detail, self.message, self.status_code, self.task
            ),
        )
