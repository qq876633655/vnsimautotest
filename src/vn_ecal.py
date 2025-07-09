# -*- coding: utf-8 -*-
"""
Time:2025/6/19 18:08
Author:yanglei
File:dd_robot.py
"""

import multiprocessing
import time
import os
import datetime
import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber
from src.proto_messages import pose_pb2
from common.log import my_log
import google.protobuf.json_format as json_format
from src.custom_error import *
import logging
from logging.handlers import RotatingFileHandler



class EcalPoseListener:
    def __init__(self, log_dir=f"../logs/{datetime.datetime.now().strftime('%Y%m%d')}/"):
        self.log_dir = log_dir
        self.vehicle_pose = multiprocessing.Manager().Value(bytes, b"")
        self.pose_buffer = multiprocessing.Manager().list()
        self.stop_event = multiprocessing.Event()
        self.process = None
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.log_dir, f"ecal.log")


        # Set up the logger with rotation
        self.logger = logging.getLogger("EcalPoseListener")
        self.logger.setLevel(logging.INFO)

        # Create a rotating file handler that writes to a log file and rotates at 10MB
        handler = RotatingFileHandler(
            self.log_file_path, maxBytes=10 * 1024 * 1024, backupCount=100
        )
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    def _listener_process(self, shared_pose, pose_buffer, stop_event, parent_pid, log_file_path):
        ecal_core.initialize([], "sim_test_listener")
        sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
        last_msg_time = multiprocessing.Value('d', time.time())

        def callback(topic_name, raw_bytes, msg):
            data_ = json_format.MessageToDict(raw_bytes)
            shared_pose.set(data_)
            now = time.time()
            pose_buffer.append((now, data_))

            with last_msg_time.get_lock():
                last_msg_time.value = now

            cutoff = now - 30
            while pose_buffer and pose_buffer[0][0] < cutoff:
                pose_buffer.pop(0)

            self.logger.info(data_)

        sub.set_callback(callback)

        while not stop_event.is_set():
            if not self._is_process_alive(parent_pid):
                my_log.info(f"主进程pid={parent_pid}意外关闭，车体位姿进程关闭pid={self.process.pid}")
                break
            time.sleep(0.01)
            now = time.time()
            with last_msg_time.get_lock():
                if now - last_msg_time.value > 1.0:
                    shared_pose.set(b"")

        ecal_core.finalize()

    def _is_process_alive(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def start(self):
        if self.process and self.process.is_alive():
            return

        os.makedirs(self.log_dir, exist_ok=True)
        parent_pid = os.getpid()
        self.stop_event.clear()
        self.process = multiprocessing.Process(
            target=self._listener_process,
            args=(self.vehicle_pose, self.pose_buffer, self.stop_event, parent_pid, self.log_file_path)
        )
        self.process.start()
        my_log.info(f"车体位姿进程开启pid={self.process.pid}，主进程pid={parent_pid}")

    def stop(self):
        self.stop_event.set()
        if self.process:
            self.process.join()
        my_log.info(f"车体位姿进程关闭pid={self.process.pid}")

    def get_latest_pose(self):
        if not self.vehicle_pose.value:
            return None
        return self.vehicle_pose.value

    def get_pose_stream(self, duration_sec=5):
        if duration_sec > 30:
            my_log.warning('最多只能拿到前面30s的位姿数据')
        now = time.time()
        start_time = now - duration_sec
        return [data for ts, data in self.pose_buffer if ts >= start_time]


def is_ecal_services_alive(timeout):
    ecal_core.mon_initialize()
    general_status = False
    slam_status = False
    perception_status = False
    slam_print_status = False
    while timeout:
        monitoring_json = ecal_core.mon_monitoring()
        if monitoring_json[1]:
            for i in monitoring_json[1]['processes']:
                if i['uname'] == 'multi_lidar_driver':
                    general_status = True
                if i['uname'] == 'Perception/Server':
                    perception_status = True
                if i['uname'] == '3DSlamPrinter':
                    slam_print_status = True
                if i['uname'] == '3dslam':
                    slam_status = True
        if general_status and slam_status and perception_status and slam_print_status:
            my_log.info('agv常用服务topic订阅成功')
            return True
        time.sleep(1)
        timeout -= 1
    raise ServiceStartError(f'agv常用服务启动失败：通用 {general_status} 感知 {perception_status} 定位可视化 {slam_print_status} 定位 {slam_status}')


def is_ecal_wbt_alive(timeout):
    """
    用手控 gui 判断 wbt 开启状态
    :param timeout:
    :return:
    """
    ecal_core.mon_initialize()
    gui_status = False
    while timeout:
        monitoring_json = ecal_core.mon_monitoring()
        if monitoring_json[1]:
            for i in monitoring_json[1]['processes']:
                if i['uname'] == 'webots_shadow_show_gui':
                    gui_status = True
        if gui_status:
            my_log.info('wbt gui 已开启')
            return True
        time.sleep(1)
        timeout -= 1
    raise WbtStartError('wbt启动失败')



if __name__ == '__main__':
    # is_ecal_services_alive(30)

    # is_ecal_wbt_alive(10)


    ecal_core.mon_monitoring()
    listener = EcalPoseListener()
    listener.start()
    num = 10
    time.sleep(2)
    while num:
        time.sleep(1)
        num -= 1
        pose = listener.get_latest_pose()
        print("当前位姿：", pose)
        if num % 10 == 0:
            print(time.time())
            print(len(listener.get_pose_stream()))
            # print(listener.get_pose_stream())
    listener.stop()


