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

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Closing hub connection")
#     hub_connection.stop()

# import time
# import threading
# import ecal.core.core as ecal_core
# from ecal.core.subscriber import ProtoSubscriber
# import sys
# import proto_messages.pose_pb2 as pose_pb2
# latest_pose = None
# last_print_time = 0
# def callback(topic_name, pose_msg, time):
#     global latest_pose
#     latest_pose = pose_msg
#
# ecal_core.initialize(sys.argv, "Simple Topic Waiter")
# sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
# sub.set_callback(callback)
# try:
#     while ecal_core.ok():
#         current_time = time.time()
#         # 每2秒打印一次最新消息
#         if current_time - last_print_time >= 2 and latest_pose is not None:
#             print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 最新 pose 消息:")
#             print(f"位置: x={latest_pose.position.x}, y={latest_pose.position.y}, z={latest_pose.position.z}")
#             last_print_time = current_time
#         time.sleep(0.1)  # 短暂休眠以减少CPU使用
#
# except KeyboardInterrupt:
#     print("用户中断...")
#
# finally:
#     # 清理
#     ecal_core.finalize()


import subprocess
import os
password = "123"
command = (
    "env LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/home/visionnav/AGVServices/lib dotnet /home/visionnav/AGVServices/robotune/robotune/VN.Robotune.dll"
)
result = subprocess.Popen(["sudo", "-S", "sh", "-c", command], cwd="/home/visionnav/AGVServices/robotune/robotune",
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = result.communicate(password + "\n")
print(stdout)
print(stderr)
# result = subprocess.Popen(["sudo", "-S", "sh", "-c", command], cwd="/home/visionnav/AGVServices/robotune/robotune",
#                           stdin=subprocess.PIPE, stdout=None, stderr=None, text=True).communicate(password + "\n")


# shutdown_path = "/home/visionnav/AGVServices/AGVPro/shutdown.sh"
# result = subprocess.run(["sudo","-S", shutdown_path],input=password + "\n", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
# print(result.stdout)
