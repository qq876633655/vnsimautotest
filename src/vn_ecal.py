# -*- coding: utf-8 -*-
"""
Time:2025/6/19 18:08
Author:yanglei
File:dd_robot.py
"""

import multiprocessing
import time
import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber
from common.log import my_log
from src.proto_messages import pose_pb2


# 全局共享数据
multi_manager = multiprocessing.Manager()
vehicle_pose = multi_manager.Value(bytes, b"")
sim_listener_process = None  # 用于跟踪子进程状态

def sim_test_ecal_listener(share_pose):
    ecal_core.initialize([], "sim_test_listener")
    sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
    while True:
        ret, msg, _, = sub.receive(100)
        share_pose.value = msg.SerializeToString()
        time.sleep(0.01)


def start_ecal_listener():
    """开启一个进程做 ecal 监听"""
    global sim_listener_process
    if sim_listener_process is None or not sim_listener_process.is_alive():
        sim_listener_process = multiprocessing.Process(target=sim_test_ecal_listener,
                                                            args=(vehicle_pose,), daemon=True)
        sim_listener_process.start()


def get_pose_once():
    """
    获取一次车体位姿
    :return:
    """
    if vehicle_pose.value:
        pose = pose_pb2.Pose()
        pose.ParseFromString(vehicle_pose.value)
        return pose
    return None


def get_pose_stream(duration_sec=20):
    """
    获取一段时间内的车体位姿
    :param duration_sec:
    :return:
    """
    poses = []
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        if vehicle_pose.value:
            pose = pose_pb2.Pose()
            pose.ParseFromString(vehicle_pose.value)
            poses.append(pose)
        time.sleep(0.01)
    return poses


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
            my_log.info('AGV常用所有服务开启')
            return True
        time.sleep(1)
        timeout -= 1
    my_log.warning(f"AGV常用服务开启状态：通用 {general_status} 感知 {perception_status} 定位可视化 {slam_print_status} 定位 {slam_status}")
    return None


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
    return None


if __name__ == '__main__':
    # is_ecal_services_alive(30)
    # is_ecal_wbt_alive(30)
    start_ecal_listener()
    time.sleep(2)
    print(get_pose_once())
    print("========================================")
    time.sleep(2)
    print(get_pose_stream())

