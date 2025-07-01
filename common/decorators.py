# -*- coding: utf-8 -*-
"""
Time:2022/2/28 19:22
Author:YANGLEI
File:decorators.py
"""

import functools
import time
import traceback
from common.my_test import MyThread
from common.log import my_log


def filter_error(func):
    """
    装饰器：在函数执行前添加时间戳

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            print("------------------%s------------------" % time.strftime("%Y-%m-%d %H:%M:%S"))
            func(*args, **kwargs)
        except Exception:
            pass

    return wrapper


def get_exceptional(func):
    """
    装饰器：方法运行异常即记录日志

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            my_log.error("\n------error func/class name: %s------\n%s"
                       % (func.__name__, traceback.format_exc()))

    return wrapper


def value_dispatch(func):
    """
    装饰器：代替 if else
    """
    registry = {}

    @functools.wraps(func)
    def wrapper(arg0, *args, **kwargs):
        try:
            delegate = registry[arg0]
        except KeyError:
            pass
        else:
            return delegate(arg0, *args, **kwargs)

        return func(arg0, *args, **kwargs)

    def register(value):
        def wrap(func):
            if value in registry:
                raise ValueError(
                    f'@value_dispatch: there is already a handler '
                    f'registered for {value!r}'
                )
            registry[value] = func
            return func

        return wrap

    wrapper.register = register
    return wrapper


def thread(state):
    """
    装饰器：方法线程

    :param state: 是否执行 thread.start()
    :return: thread 实例化
    """

    def wrapper(func):
        def inner(*args, **kwargs):
            t = MyThread(target=func, args=args, kwargs=kwargs)
            # if kwargs["daemon"]:
            #     t.setDaemon(True)
            if state == "start":
                t.start()
            return t
        return inner
    return wrapper


@thread("")
def greeting(name, daemon=None):
    print(f'你好啊，{name}！')
    time.sleep(1)
    print(f'再见了，{name}.')
    return "1"


if __name__ == "__main__":
    a = greeting('老张')
    b = greeting('小李', daemon=True)
    c = greeting('老刘')
    a.start()
    b.start()
    b.join()
    c.start()
    print(a.get_result())
    # @get_exceptional
    # def test(i, m, w):
    #     print(i / m + w)
    #
    #
    # while True:
    #     f = random.choice([0, 1, 2, 3])
    #     n = random.choice([0, 1, 2, 3])
    #     q = random.choice([0, 1, 2, 3])
    #     test(f, n, q)
    #     time.sleep(0.3)

    # greeting('老张')
    # greeting('小李').join()
    # greeting('老刘')
