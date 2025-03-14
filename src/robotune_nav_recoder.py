# coding=utf-8
import requests
import sys
import time
import threading
import csv
import os
import numpy as np
import math

import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber

import proto_messages.pose_pb2 as pose_pb2

# from robotune_apis import *


# 配置
CSV_FILE_PREFIX = "data"
MAX_FILE_SIZE_MB = 100
CURRENT_FILE = ''
BATCH_SIZE = 100  # 每批写入的消息数量  

FLAG_RECODE = False

headers = {
    "accept": "text/plain",
    "Authorization": "null",
    "X-XSRF-TOKEN": "CfDJ8CLpIqq3xxxLjgPMz28yvcIkcamlefVJLtByKCRcVYrCtUzZm_AqTXSiTnvmwWWaMZKLTgWSeeNFkSEpaVQyoo0ROkc0IRcHPPYC0h8svmAL5QxqxoEBgeNbmjBlyhydWV_NcabN1GdL0i_-Zjkm7mg",
}


def quaternion_to_axis_angle(q):
    """
    将四元数转换为轴角表示（仅依赖NumPy）
    
    参数：
        q : numpy数组，形状为(4,)或(N,4)，四元数格式为 [x, y, z, w]
    
    返回：
        axis : 单位旋转轴，形状为(3,)或(N,3)
        angle : 旋转角度（弧度），形状为()或(N,)
    """
    # 确保输入为NumPy数组
    q = np.asarray(q)
    
    # 提取四元数分量（假设输入为 [x, y, z, w] 格式）
    x, y, z, w = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    
    # 计算旋转角度（弧度）
    angle = 2 * np.arccos(w)
    
    # 计算旋转轴的分母项 sin(theta/2)
    sin_half_theta = np.sqrt(1 - w**2)  # 等价于 sqrt(x² + y² + z²)
    
    # 处理除零问题（当角度接近0时，轴方向无意义，设为默认轴[1,0,0]）
    epsilon = 1e-7  # 极小值阈值
    safe_sin = np.where(sin_half_theta > epsilon, sin_half_theta, 1.0)
    
    # 计算归一化旋转轴
    axis_x = np.where(sin_half_theta > epsilon, x / safe_sin, 1.0)
    axis_y = np.where(sin_half_theta > epsilon, y / safe_sin, 0.0)
    axis_z = np.where(sin_half_theta > epsilon, z / safe_sin, 0.0)
    
    # 合并轴分量
    axis = np.stack([axis_x, axis_y, axis_z], axis=-1)
    
    return axis, angle


# 获取当前文件路径
def get_current_file_path():
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    return f"{CSV_FILE_PREFIX}_{current_time}.csv"


# 检查文件大小并切换文件
def check_and_switch_file(file_path):
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        if file_size >= MAX_FILE_SIZE_MB:
            CURRENT_FILE = get_current_file_path()
            return CURRENT_FILE
    return file_path


# 写入文件的线程
def write_to_file():
    global messages_buffer
    global CURRENT_FILE
    CURRENT_FILE = get_current_file_path()
    while True:
        if messages_buffer:
            file_path = check_and_switch_file(CURRENT_FILE)

            with open(file_path, mode="a", newline="", buffering=1) as file:
                writer = csv.writer(file)
                while messages_buffer:
                    print(messages_buffer)
                    row_list_w = messages_buffer.pop(0)
                    print(row_list_w)
                    writer.writerow(row_list_w)

        time.sleep(0.1)  # 减少 CPU 占用


# 回调函数，处理接收到的消息
def on_message(topic_name, msg, msg_time):
    global messages_buffer
    global FLAG_RECODE
    row_list = []
    if not FLAG_RECODE:
        return

    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    # 单个四元数转轴角
    q = np.array([msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w])  # [x, y, z, w] = [0, 0, 0.707, 0.707]
    axis, angle = quaternion_to_axis_angle(q)
    # print("Axis:", axis)        # 输出: [0. 0. 1.]
    # print("Angle (rad):", angle) # 输出: 1.5708 (≈π/2)

    row_list.extend([current_time, round(msg.position.x, 4), round(msg.position.y, 4), round(msg.position.z, 4)])
    row_list.extend(
        [
            axis[0],
            axis[1],
            axis[2],
            angle,
        ]
    )

    # 获取当前位置
    GetCurrentPos_url = "http://127.0.0.1:24311/api/services/map/Agv/GetCurrentPos"
    # 请求该接口
    GetCurrentPos_response = requests.get(GetCurrentPos_url, headers=headers)
    # 获取响应数据，并解析JSON，转化为python字典
    GetCurrentPos_result = GetCurrentPos_response.json()
    # 打印响应状态码
    # print(GetCurrentPos_response.status_code)
    # print(GetCurrentPos_result['result'])


    row_list.extend(
        [
            GetCurrentPos_result["result"]["x"],
            GetCurrentPos_result["result"]["y"],
            GetCurrentPos_result["result"]["theta"],
        ]
    )

    # 获取当前机器人状态
    CurrentAgvRunStatusInfo_url = (
        "http://127.0.0.1:24311/api/services/task/Agv/CurrentAgvRunStatusInfo"
    )
    CurrentAgvRunStatusInfo_response = requests.post(
        CurrentAgvRunStatusInfo_url, headers=headers
    )
    CurrentAgvRunStatusInfo_result = CurrentAgvRunStatusInfo_response.json()
    # print(CurrentAgvRunStatusInfo_result['result']['lastEndControlError'])
    # print(type(CurrentAgvRunStatusInfo_result['result']['lastEndControlError']))

    if isinstance(CurrentAgvRunStatusInfo_result["result"]["lastEndControlError"], str):
        result = CurrentAgvRunStatusInfo_result["result"]["lastEndControlError"].split(
            ","
        )
        row_list.extend(result)

    # url_GetCurrentTaskInfo = (
    #     "http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo"
    # )
    # reponse_GetCurrentTaskInfo = requests.get(url_GetCurrentTaskInfo, headers=headers)
    # result_GetCurrentTaskInfo = reponse_GetCurrentTaskInfo.json()
    # print("task name = ", result_GetCurrentTaskInfo["result"]["taskId"])
    # row_list.extend(result_GetCurrentTaskInfo["result"]["taskId"])

    messages_buffer.append(row_list)

    FLAG_RECODE = False


def listen(taskName):
    global FLAG_RECODE

    url_GetCurrentTaskInfo = (
        "http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo"
    )
    reponse_GetCurrentTaskInfo = requests.get(url_GetCurrentTaskInfo, headers=headers)
    result_GetCurrentTaskInfo = reponse_GetCurrentTaskInfo.json()

    if not isinstance(result_GetCurrentTaskInfo["result"], dict):
        print("任务未开始")
        return result_GetCurrentTaskInfo["result"]["name"]
    elif result_GetCurrentTaskInfo["result"]["name"] != "CommonWaitting":
        print("不是通用等待任务")
        return result_GetCurrentTaskInfo["result"]["name"]    
    elif result_GetCurrentTaskInfo["result"]["name"] == taskName:
        print("和上个任务相同，不记录")
        return result_GetCurrentTaskInfo["result"]["name"]    
    elif result_GetCurrentTaskInfo["result"]["taskStatus"] == "transacting":
        print("记录相关信息")
        FLAG_RECODE = True
        return result_GetCurrentTaskInfo["result"]["name"]


if __name__ == "__main__":

    # 登录，获取控制权，触发任务，记录数据

    print("监听记录信号：执行等待任务中时记录信息")
    interval_time = 2
    taskName = ""

    ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")

    # csv表头
    CSV_HEADER = [
        "time",
        "x",
        "y",
        "z",
        "rotation_x",
        "rotation_y",
        "rotation_z",
        "rotation_angle",
        "slam_x",
        "slam_y",
        "slam_theta",
        "lastEndControlError_x",
        "lastEndControlError_y",
        "lastEndControlError_theta",
    ]

    # 创建消息缓冲区
    messages_buffer = [ CSV_HEADER ]

    # 创建并启动写入文件的线程
    write_thread = threading.Thread(target=write_to_file, daemon=True)
    write_thread.start()

    sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
    sub.set_callback(on_message)

    print(f"间隔时间： {interval_time} s")
    while True:
        try:
            taskName = listen(taskName)
            # print(taskName)
            time.sleep(interval_time)
        except KeyboardInterrupt:
            # 关闭 eCAL
            ecal_core.finalize()
            print("程序被用户中断")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")
            continue
