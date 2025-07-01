# -*- coding: utf-8 -*-
"""
Time:2022/3/22 14:25
Author:YANGLEI
File:my_test.py
"""

import threading

# 定义一个MyThread.py线程类
class MyThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None, *, daemon=None):
        super(MyThread, self).__init__()
        self._target = target
        self._args = args if args is not None else []
        self._kwargs = kwargs if kwargs is not None else {}
        self._result = None
        if daemon is not None:
            self._daemonic = daemon
        else:
            self._daemonic = threading.current_thread().daemon

    def run(self):
        self._result = self._target(*self._args, **self._kwargs)  # 在执行函数的同时，把结果赋值给result,
        # 然后通过get_result函数获取返回的结果

    def get_result(self):
        try:
            return self._result
        except Exception as e:
            return None


class MyTimer(threading.Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        super(MyTimer, self).__init__(interval, function, args=None, kwargs=None)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()
        self.result = None

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.result = self.function(*self.args, **self.kwargs)  # 在执行函数的同时，把结果赋值给result,
        self.finished.set()

    # 然后通过get_result函数获取返回的结果
    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None
