# from signalrcore.hub_connection_builder import HubConnectionBuilder
# import time
# import logging
#
# hub_url = 'ws://127.0.0.1:24311/signalr'
#
# hub_connection = HubConnectionBuilder()\
#     .with_url(hub_url)\
#     .configure_logging(logging.DEBUG)\
#     .build()
#
# def on_receive(data):
#     print(data)
#
# hub_connection.on('receive', on_receive)
#
# hub_connection.start()
# print('connect success')
# hub_connection.send('11', ['11', '22'])
# import requests
import time

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Closing hub connection")
#     hub_connection.stop()

# import subprocess
#
# SUDO_PWD = '123'
# cmd = "sudo -S /home/visionnav/AGVServices/AGVPro/startupRobotune.sh"
# result = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
#                           text=True)
# result.stdin.write("123\n")
# result.stdin.flush()
# print(result.stdout)

##############################################################################
# from src.vn_ecal import *
#
# listener = EcalPoseListener()
# listener.start()
# print(listener.process.pid)
# num = 30
# time.sleep(2)
# while num:
#     time.sleep(1)
#     num -= 1
#     pose = listener.get_latest_pose()
#     print("当前位姿：", pose)
#     if num == 20 or num == 10:
#         print(time.time())
#         print(len(listener.get_pose_stream()))
#         print(listener.get_pose_stream())
# listener.stop()
# time.sleep(2)
# listener.get_latest_pose()
##############################################################################
# import math
#
#
# def quaternion_to_euler(q):
#     w = q[0]
#     x = q[1]
#     y = q[2]
#     z = q[3]
#     yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
#     pitch = math.asin(2 * (w * y - x * z))
#     roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
#     return roll, pitch, yaw
#
#
# # 示例四元数
# quaternion = [0, 0.7068252, 0, 0.7073883]
#
# # 转换为旋转轴和角度
# roll, pitch, yaw = quaternion_to_euler(quaternion)
#
# print(f"Rotation {roll, pitch, yaw}")
##############################################################################
# import math
# import numpy as np
#
#
# def quat_to_axis_angle(quat):
#     # 四元数标准化
#     quat = quat / np.linalg.norm(quat)
#
#     # 实部对应角度
#     angle = 2 * math.acos(quat[0])
#
#     # 虚部对应旋转轴
#     axis = quat[1:] / math.sin(angle / 2)
#
#     return axis, angle
#
#
# # 示例四元数
# quaternion = np.array([0.35535, 0.46194, 0.13583, 0.80175])
#
# # 转换为旋转轴和角度
# axis, angle = quat_to_axis_angle(quaternion)
#
# print(f"Rotation axis: {axis}, Angle: {angle}")
##############################################################################
# def timestamp_to_formatted_time(timestamp):
#     """
#     将时间戳（毫秒）转换为格式化的时间字符串（精确到毫秒）
#     """
#     error_sec = timestamp // 1000
#     error_ms = timestamp % 1000
#     dt_object = datetime.datetime.fromtimestamp(error_sec)
#     formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
#     return f"{formatted_time}.{error_ms:03d}"
##############################################################################
from multiprocessing import Process
import time, os
from common.log import my_log
def worker(parent_pid):
    print(f"worker started. pid={os.getpid()}")
    while True:
        if not is_process_alive(parent_pid):
            break
        my_log.info(f"worker pid={os.getpid()}")
        time.sleep(1)

def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

if __name__ == '__main__':
    pid = os.getpid()
    p = Process(target=worker, args=(pid,))
    p.start()
    time.sleep(2)
    print('main process exiting')
    os._exit(1)