from __future__ import annotations

import inspect
from typing import List


class Logger:
    """
    Please refer to existing children classes if you want to make a new one
    """
    active_loggers: List[Logger] = []

    def __init__(self, disable=False):
        self.log_list = []
        # the path of the file that calls this function
        self.caller_list = []
        self.disable = True if disable != False else False

    def add_log(self, log: any, stack_depth=0):
        caller_path = inspect.stack()[stack_depth + 1].filename
        self.caller_list.append(caller_path)
        self.log_list.append(log)

    @classmethod
    def add_log_to_all(cls, log: any, stack_depth=0):
        for logger in cls.active_loggers:
            logger.add_log(log, stack_depth + 1)

    def __enter__(self):
        if self.disable:
            return self
        # Add self to active_loggers
        self.__class__.active_loggers.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.disable:
            return self
        self.__class__.active_loggers.remove(self)
        self.display_log()

    def display_log(self):
        raise NotImplementedError
