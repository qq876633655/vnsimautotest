# -*- coding: utf-8 -*-
"""
Time:2022/8/14 13:13
Author:YANGLEI
File:utils.py
"""

import sys
sys.path.append("/home/visionnav/VNSim/vnsimautotest")
import os
import math
import transforms3d as tf
from scipy.spatial.transform import Rotation
import numpy as np
from math import sqrt
import plotly.graph_objects as go
from common.log import my_log


class Pose:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, roll: float = 0.0, pitch: float = 0.0,
                 yaw: float = 0.0):
        """
        位姿，包含位移信息和旋转信息

        :param x: 长度
        :param y:
        :param z:
        :param roll: 角度
        :param pitch:
        :param yaw:
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.roll = float(roll)
        self.pitch = float(pitch)
        self.yaw = float(yaw)


def axis_angle_to_rpy(translation_, rotation_):
    """
    wbt 中物体位姿转成欧拉角返回一个 Pose
    :param translation_:
    :param rotation_:
    :return:
    """
    axis = np.array(rotation_[:3])
    angle = rotation_[3]

    r = Rotation.from_rotvec(axis * angle)
    roll, pitch, yaw = r.as_euler('xyz', degrees=True)
    x, y, z = translation_
    wbt_pose = Pose(x, y, z, roll, pitch, yaw)

    return wbt_pose


def rpy_to_axis_angle(roll, pitch, yaw):
    """
    物体位姿转 wbt 中 4 元组
    :param roll:
    :param pitch:
    :param yaw:
    :return:
    """
    r = Rotation.from_euler('xyz', [roll, pitch, yaw], degrees=True)
    rotvec = r.as_rotvec()
    angle = np.linalg.norm(rotvec)
    if angle == 0:
        axis = [0, 0, 1]
    else:
        axis = (rotvec / angle).tolist()
    return axis + [angle]


def eulerAngles2rotationMat(theta, format='degree'):
    """
    Calculates Rotation Matrix given euler angles.
    :param theta: 1-by-3 list [rx, ry, rz] angle in degree
    :return:
    RPY角，是ZYX欧拉角，依次 绕定轴XYZ转动[rx, ry, rz]
    """
    if format == 'degree':
        theta = [i * math.pi / 180.0 for i in theta]

    R_x = np.array([[1, 0, 0],
                    [0, math.cos(theta[0]), -math.sin(theta[0])],
                    [0, math.sin(theta[0]), math.cos(theta[0])]
                    ])

    R_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                    [0, 1, 0],
                    [-math.sin(theta[1]), 0, math.cos(theta[1])]
                    ])

    R_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                    [math.sin(theta[2]), math.cos(theta[2]), 0],
                    [0, 0, 1]
                    ])
    R = np.dot(R_z, np.dot(R_y, R_x))  # xyz 定轴
    # R = np.dot(R_x, np.dot(R_y, R_z))  # xyz 动轴
    return R


def get_a_c_pose(a_b: Pose, b_c: Pose) -> Pose:
    """
    已知 a 坐标系下 b 位姿，已知 b 坐标系下 c 位姿，获取 a 坐标系下 c 点位姿

    :param a_b:
    :param b_c:
    :return:
    """
    a_c = Pose()
    r_a_b = eulerAngles2rotationMat([a_b.roll, a_b.pitch, a_b.yaw])
    t_a_b = np.array([a_b.x, a_b.y, a_b.z])
    r_b_c = eulerAngles2rotationMat([b_c.roll, b_c.pitch, b_c.yaw])
    t_b_c = np.array([b_c.x, b_c.y, b_c.z])

    r_a_c = np.dot(r_a_b, r_b_c)
    t_a_c = np.dot(r_a_b, t_b_c) + t_a_b

    a_c.x, a_c.y, a_c.z = t_a_c

    a_c.roll, a_c.pitch, a_c.yaw = np.degrees(tf.euler.mat2euler(r_a_c, 'sxyz'))
    return a_c


def get_c_b_pose(a_b: Pose, a_c: Pose):
    """
    已知 a 坐标系下 b 位姿，已知 a 坐标系下 c 位姿，获取 c 坐标系下 b 点位姿
    当 a_b 全为 0 时，可以获取 c 坐标系下 a 位姿

    :param a_b:
    :param a_c:
    :return:
    """
    # 将位移向量和欧拉角转换为 numpy 数组
    a_b_translation = np.array([a_b.x, a_b.y, a_b.z])
    a_b_euler = np.array([a_b.roll, a_b.pitch, a_b.yaw])
    a_c_translation = np.array([a_c.x, a_c.y, a_c.z])
    a_c_euler = np.array([a_c.roll, a_c.pitch, a_c.yaw])

    # 构造旋转矩阵
    a_b_rotation_matrix = Rotation.from_euler('xyz', a_b_euler, degrees=True).as_matrix()
    a_c_rotation_matrix = Rotation.from_euler('xyz', a_c_euler, degrees=True).as_matrix()

    # 计算点 A 相对于以点 B 为原点的坐标系中的位移
    a_b_relative_translation = a_b_translation - a_c_translation

    # 计算点 A 相对于以点 B 为原点的坐标系中的旋转矩阵
    relative_rotation_matrix = np.dot(a_c_rotation_matrix.T, a_b_rotation_matrix)

    # 将旋转矩阵转换为欧拉角
    relative_euler = Rotation.from_matrix(relative_rotation_matrix).as_euler('xyz', degrees=True)
    c_b = Pose(x=a_b_relative_translation.tolist()[0],
               y=a_b_relative_translation.tolist()[1],
               z=a_b_relative_translation.tolist()[2],
               roll=relative_euler.tolist()[0],
               pitch=relative_euler.tolist()[1],
               yaw=relative_euler.tolist()[2])

    return c_b


def create_dir(path):
    """
    创建目录

    :param path:
    :return:
    """
    if not os.path.exists(path):
        my_log.info("创建目录：%s" % path)
        os.makedirs(path)
    return path


def safe_deceleration(v_current, a_min, a_max, driving_a_virtual, warning_a_virtual, warning_area=None):
    """
    安全减速公式

    :param v_current: 当前车速
    :param a_min: 最小减速度
    :param a_max: 最大减速度
    :param driving_a_virtual: 行驶区域虚拟减速度
    :param warning_a_virtual: 告警区域虚拟减速度
    :param warning_area: 是否在告警区域
    :return:
    """
    a_virtual = warning_a_virtual if warning_area else driving_a_virtual
    # print(a_virtual)
    d_lst = [i / 10 for i in range(1, 51)]
    print(d_lst)
    v_result_lst = []
    for d in d_lst:
        # 先根据当前速度，常规减速度，紧急减速度，障碍物距离计算出危险系数 f
        f = (((math.pow(v_current, 2)) / (2 * a_min)) - d) \
            / (((math.pow(v_current, 2)) / (2 * a_min)) - ((math.pow(v_current, 2)) / (2 * a_max)))
        # 已知障碍物所在区域，如果在告警区域，f 先乘以 0.8，如果 f 小于 0 按 0 计算，如果 f 大于 0.9 按 0.9 计算
        if warning_area:
            f *= 0.8
            if f < 0:
                f = 0
            elif f > 0.9:
                f = 0.9
        # 不再告警区域，则处于行驶区域，f 小于 0 按 0 计算，如果 f 大于 1 按 1 计算
        else:
            if f < 0:
                f = 0
            elif f > 1:
                f = 1
        # print(d, f)
        try:
            # 根据虚拟减速度计算出建议速度
            v_result = sqrt(2 * (1 - f) * a_virtual * d)
        except ValueError:
            break
        v_result_lst.append(round(v_result, 2))

    fig = go.Figure()  # 声明fig为一个图表
    fig.add_trace(go.Scatter(  # 通过add_trace，往图表中加入折线。折线是go.Scatter类
        x=d_lst,
        y=v_result_lst
    ))
    fig.show()  # 展示图表


def channel_width_and_speed():
    a_max = 1  # 零减速度
    a_min = 0.3  # 非零减速度
    a_virtual = 0.2  # 虚拟减速度
    vehicle_width = 1.09  # 车体宽度
    vehicle_axial_length = 1.33  # 车轴长度（车体中心到车前）
    vehicle_length = 2.565  # 车长（叉车到车前）
    prong_length = 1.2  # 叉尖长度（车体中心到叉尖）
    e_f, e_b, e_l, e_r = 0.1, 0.1, 0.1, 0.1  # 前后左右膨胀距离
    channel_width = 1.6  # 通道宽度
    curve_a = 3.08  # 曲率
    d_y = channel_width / 2  # 障碍物最近y距离
    w_2 = vehicle_width / 2  # 车半宽
    d_x = sqrt((4 * math.pow(curve_a, 2) * math.pow(d_y, 2)) / vehicle_width - math.pow(curve_a, 2))
    print(f"最小坐标点：({d_x}, {d_y})")
    if d_x <= vehicle_axial_length:
        front_channel_vehicle_width = d_y - w_2
    else:
        front_channel_vehicle_width = sqrt(math.pow((d_x - vehicle_axial_length - e_f), 2) +
                                           math.pow((d_y - w_2 - e_r), 2))
    if d_x <= prong_length:
        back_channel_vehicle_width = d_y - w_2
    else:
        back_channel_vehicle_width = sqrt(math.pow((d_x - prong_length - e_b), 2) +
                                          math.pow((d_y - w_2 - e_r), 2))
    print(f"前方通道和车体距离：{front_channel_vehicle_width}")
    print(f"后方通道和车体距离：{back_channel_vehicle_width}")
    front_v = sqrt(2 * a_virtual * front_channel_vehicle_width)
    back_v = sqrt(2 * a_virtual * back_channel_vehicle_width)
    print(f"前方建议速度：{front_v}")
    print(f"后方建议速度：{back_v}")


def parse_string_to_list(s):
    s = s.strip()
    if not s:
        return []
    if ',' in s:
        return [item.strip() for item in s.split(',') if item.strip()]
    return [s]


def cal_get_vehicle_pose(translation_, rotation_, card_length, loadpositionx, cut_off_x=0, same_direction=True):
    """
    计算取载具时的预期车体位姿，需要保证载具 x 轴是入叉面
    :param cut_off_x:
    :param translation_:
    :param rotation_:
    :param card_length:
    :param loadpositionx:
    :param same_direction:
    :return:
    """
    card_pose = axis_angle_to_rpy(translation_, rotation_)
    if same_direction:
        x_ = card_length / 2 - loadpositionx + cut_off_x
    else:
        x_ = -(card_length / 2 - loadpositionx + cut_off_x)
    offset_pose = Pose(x_)
    expected_pose = get_a_c_pose(card_pose, offset_pose).__dict__
    print(expected_pose)
    return expected_pose


def cal_put_vehicle_pose(storage_pose, card_length, card_width, loadpositionx, perception_type, cut_off_x=0,
                         left_obs_dis=0, right_obs_dis=0, backward_obs_dis=0, storage_cross_x_dis=0, storage_cross_yaw=0,
                         put_offset_x=0, put_offset_y=0,  min_safe_dist_x=0.02, min_safe_dist_y=0.02):
    """
    计算放载具时的预期车体位姿，需要保证载具 x 轴是入叉面
    固定放货法：计算车中心和库位x的偏差
    空间、后置、前置：计算车体中心和库位y的偏差
    后置：计算库位和后方障碍物的偏差
    前置：计算库位和横梁的偏差
    :param storage_pose: 放货库位中心点坐标，x、y、yaw
    :param card_length:
    :param card_width:
    :param loadpositionx:
    :param perception_type:
    :param left_obs_dis: 库位中心点到左侧障碍物的距离
    :param right_obs_dis: 库位中心点到右侧障碍物的距离
    :param backward_obs_dis: 库位中心点到后侧障碍物的距离
    :param storage_cross_x_dis: 库位中心点到横梁前表面的距离
    :param storage_cross_yaw: 库位和横梁的 yaw
    :param put_offset_x:
    :param put_offset_y:
    :param cut_off_x: 取货不到位
    :param min_safe_dist_x:
    :param min_safe_dist_y:
    :return:
    """

    offset_pose = Pose()
    offset_x = card_length / 2 - loadpositionx + cut_off_x
    offset_y = 0
    if perception_type == 0:
        pass
    # Todo 空间计算中的当两侧障碍物逻辑还没写
    if perception_type == 1 or perception_type == 2 or perception_type == 3 or perception_type == 6:
        left_right_dis = put_offset_y if put_offset_y >= min_safe_dist_y else min_safe_dist_y
        if left_obs_dis > 0:
            offset_y = left_obs_dis - (card_width / 2 + left_right_dis)
        if right_obs_dis > 0:
            offset_y = (card_width / 2 + left_right_dis) - right_obs_dis
        if left_obs_dis > 0 and right_obs_dis > 0:
            pass
    if perception_type == 2:
        if put_offset_x >= min_safe_dist_x:
            offset_x += (card_length / 2 + put_offset_x) - backward_obs_dis
        if put_offset_x < min_safe_dist_x:
            offset_x += (card_length / 2 + min_safe_dist_x) - backward_obs_dis
    if perception_type == 3 or perception_type == 6:
        if put_offset_x >= min_safe_dist_x:
            offset_x += storage_cross_x_dis - card_length / 2 + put_offset_x
        if put_offset_x < min_safe_dist_x:
            offset_x += storage_cross_x_dis - card_length / 2 + min_safe_dist_x
    offset_pose.x = offset_x
    offset_pose.y = offset_y
    offset_pose.yaw = storage_cross_yaw

    expected_pose = get_a_c_pose(storage_pose, offset_pose).__dict__
    print(expected_pose)
    return expected_pose


if __name__ == '__main__':
    translation_ = [92.85, 157.2, 0]
    # rotation_ = [0, 0, 1, -1.4]
    rotation_ = [0.0, 0.0, -1.0, 1.3962634015954636]
    # print(axis_angle_to_rpy(translation_, rotation_).__dict__)
    # {'x': 92.85, 'y': 157.2, 'z': 0.0, 'roll': 0.0, 'pitch': 0.0, 'yaw': -80.21409131831524}
    # {'x': 92.85, 'y': 157.2, 'z': 0.0, 'roll': 0.0, 'pitch': 0.0, 'yaw': -80.0}
    print(rpy_to_axis_angle(roll=0, pitch=0, yaw=-80))


    # card_length = 1
    # card_width = 1
    # loadpositionx = -0.2
    # cal_get_vehicle_pose(translation, rotation, card_length, loadpositionx, same_direction=True)
    # storage_pose = Pose(x=100,y=100, yaw=-90)
    # cal_put_vehicle_pose(storage_pose=storage_pose,card_length=card_length,card_width=card_width,
    #                      loadpositionx=loadpositionx, perception_type=3, storage_cross_x_dis=1.1,
    #                      put_offset_x=0.1)

    # safe_deceleration(0.6, 0.3, 1, 0.2)
    # safe_deceleration(0.6, 0.3, 1, 0.2, 0.5, None)
    # channel_width_and_speed()
    # import psutil
    #
    # # 获取进程对象
    # p = psutil.Process(28180)
    #
    # # 获取 CPU 占用率（单位：百分比）
    # while True:
    #     cpu_percent = p.cpu_percent(interval=1)
    #
    #     # 获取内存占用情况（单位：字节）
    #     memory_info = p.memory_info()
    #     rss = memory_info.rss  # 常驻内存大小
    #     vms = memory_info.vms  # 虚拟内存大小
    #
    #     # 获取磁盘 I/O 信息（单位：字节/秒）
    #     io_counters = p.io_counters()
    #     read_bytes = io_counters.read_bytes  # 读取字节数
    #     write_bytes = io_counters.write_bytes  # 写入字节数
    #     print(cpu_percent, rss, vms, read_bytes, write_bytes)
