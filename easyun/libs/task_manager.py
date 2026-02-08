# -*- coding: utf-8 -*-
"""
  @module:  Simple async task manager
  @desc:    Replaces Celery with threading + in-memory task store
"""
import uuid
import threading
from datetime import datetime


class TaskState:
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    PROGRESS = 'PROGRESS'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class TaskResult:
    def __init__(self, task_id):
        self.id = task_id
        self.status = TaskState.PENDING
        self.info = {}

    def ready(self):
        return self.status in (TaskState.SUCCESS, TaskState.FAILURE)

    def update_state(self, state, meta=None):
        self.status = state
        if meta:
            self.info.update(meta)


# Global task store
_tasks = {}
_lock = threading.Lock()


def get_task(task_id):
    with _lock:
        return _tasks.get(task_id)


def run_async(func, app, *args):
    """Run a function in a background thread with Flask app context.

    Returns a TaskResult that can be queried for status/progress.
    """
    task_id = str(uuid.uuid4())
    result = TaskResult(task_id)
    with _lock:
        _tasks[task_id] = result

    def wrapper():
        with app.app_context():
            try:
                ret = func(result, *args)
                if result.status != TaskState.FAILURE:
                    result.status = TaskState.SUCCESS
                if ret:
                    result.info.update(ret)
            except Exception as ex:
                result.status = TaskState.FAILURE
                result.info['message'] = str(ex)

    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    return result
