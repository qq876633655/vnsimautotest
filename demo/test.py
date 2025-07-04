# import time
# from common.utils import axis_angle_to_rpy
# from src.ecal_data import get_pose_stream, get_pose_once, start_ecal_listener
#
# start_ecal_listener()
#
#
# while True:
#     time.sleep(2)
#     pose = get_pose_once()
#     print(pose)


# import multiprocessing
# import time
# import ecal.core.core as ecal_core
# from ecal.core.subscriber import ProtoSubscriber
# from src.proto_messages import pose_pb2
#
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
#             print(latest_pose)
#             # print(f"位置: x={latest_pose.position.x}, y={latest_pose.position.y}, z={latest_pose.position.z}")
#             last_print_time = current_time
#         time.sleep(0.1)  # 短暂休眠以减少CPU使用
#
# except KeyboardInterrupt:
#     print("用户中断...")
#
# finally:
#     # 清理
#     ecal_core.finalize()

import json
import paho.mqtt.client as mqtt
import time

# 存储错误码数据
latest_error_code = None


# 回调函数：连接时调用
def on_connect(client, userdata, flags, rc):
    print(f"连接成功，返回码 {rc}")
    # 连接后订阅错误码的主题
    client.subscribe("agv/v1/c/errorCode")


# 回调函数：消息到达时调用
def on_message(client, userdata, msg):
    global latest_error_code
    print(f"收到错误码消息：{msg.topic} -> {msg.payload.decode()}")

    try:
        # 解析并保存最新的错误码
        latest_error_code = json.loads(msg.payload.decode())
        print("最新的错误码：", latest_error_code)
    except json.JSONDecodeError:
        print("收到的消息不是有效的 JSON 格式")


def subscribe_error_code():
    # 创建 MQTT 客户端
    client = mqtt.Client(client_id="error_code_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    # 连接到 MQTT 代理
    client.connect("localhost", 1883, 60)

    # 启动 MQTT 客户端循环，开始监听
    client.loop_start()

    # 持续运行并监听错误码，直到手动停止
    try:
        while True:
            time.sleep(1)
            # 在这里你可以调用获取最新错误码的方法
            if latest_error_code:
                print("当前错误码：", latest_error_code)
            else:
                print("无错误码数据")
    except KeyboardInterrupt:
        print("退出错误码订阅")
        client.loop_stop()


