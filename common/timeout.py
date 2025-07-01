# -*- coding: utf-8 -*-
"""
Time:2022/8/1 9:35
Author:yanglei
File:timeout.py
"""

import time


class Timeout:
    def __init__(self, duration):
        """
        超时

        :param duration: 持续时间
        """
        self._duration = duration
        self.new_time = int(time.time() + self._duration) if self._duration else None
        self.now_time = time.time()
        # 是否重新定时
        self.restart_ = True
        # 倒计时
        self.count_down = self._duration

    def if_timeout(self) -> bool:
        """
        是否超时

        :return: 超时返回 True
        """
        if self.new_time:
            self.count_down = self.new_time - int(time.time())
            return (self.new_time - int(time.time())) <= 0
        else:
            return False

    def restart(self, duration):
        """
        重新定时

        :param duration: 定时时间
        :return:
        """
        self.new_time = int(time.time() + duration)


if __name__ == '__main__':
    timeout = Timeout(10)
    while True:
        print(timeout.count_down)
        time.sleep(1)
        if timeout.count_down <= 5 and timeout.restart_:
            timeout.restart(10)
            timeout.restart_ = None
        if timeout.if_timeout():
            print("finish")
            break
