# -*- coding: utf-8 -*-
"""
Time:2021/6/29 13:28
Author:YANGLEI
File:log.py
"""

import os
import time
import logging


class Log:
    def __init__(self):
        """
        日志记录
        """
        self.log_path = os.path.join(os.path.dirname(__file__), '../logs')
        self.log_name = os.path.join(self.log_path, f"{time.strftime('%Y-%m-%d')}.log")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 创建一个 handler，用于写入日志文件
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # 再创建一个 handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        # 给 logger 添加 handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


my_log = Log()

if __name__ == '__main__':
    my_log.debug('test debug')
    my_log.info('test info')
    my_log.warning('test warning')
    my_log.error('test error')
    my_log.critical('test critical')