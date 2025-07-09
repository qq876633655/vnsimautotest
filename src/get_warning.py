# import json
# import time
# from datetime import datetime
#
# import paho.mqtt.client as mqtt
# import threading
#
# latest_error_code_lst = None
#
#
# # 回调函数：连接时调用
# def on_connect(client, userdata, flags, rc, properties):
#     print(f"连接成功，返回码 {rc}")
#     # 连接后订阅错误码的主题
#     client.subscribe("agv/v1/c/auto_test/general/diagnosis/getLastDiagnosicInfo")
#     # client.subscribe("agv/v1/c/webClient_common_diagnosis/general/diagnosis/getLastDiagnosicInfo")
#
#
# # 回调函数：消息到达时调用
# def on_message(client, userdata, msg):
#     global latest_error_code_lst
#     try:
#         latest_error_code_lst = json.loads(msg.payload.decode())['payload']['errorcodes']
#     except json.JSONDecodeError:
#         print("收到的消息不是有效的 JSON 格式")
#
#
# def subscribe_error_code():
#     client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="auto_test")
#     current_time = datetime.fromtimestamp(time.time())
#     formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.") + str(current_time.microsecond)[:3] + "Z"
#     payload = {
#         "method": "getLastDiagnosicInfo",
#         "srcAddr": "auto_test",
#         "seq": "065db26e-f16f-cb64-9d8f-c784774c59a2",
#         "version": "1.0.1",
#         "timestamp": formatted_time
#     }
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect("localhost", 1883, 60)
#     client.loop_start()
#     try:
#         while True:
#             # pass
#             client.publish('agv/v1/s/general/diagnosis/getLastDiagnosicInfo', payload=json.dumps(payload), qos=1)
#             time.sleep(2)
#     except KeyboardInterrupt:
#         print("退出错误码订阅")
#         client.loop_stop()
#
#
# def start_thread_error_code():
#     error_code_thread = threading.Thread(target=subscribe_error_code)
#     error_code_thread.daemon = True  # 设置为守护线程，主进程退出时自动退出
#     error_code_thread.start()
#
#
# if __name__ == '__main__':
#     start_thread_error_code()
#     num = 100
#     while num:
#         print(latest_error_code_lst)
#         time.sleep(2)
#         num -= 1
# error_code_listener.py

import json
import os

import paho.mqtt.client as mqtt
import threading
from datetime import datetime
import time

from common.log import my_log


class ErrorCodeSubscriber:
    def __init__(self, broker_host='localhost', broker_port=1883):
        self.latest_error_code = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="auto_test_error_code")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker_host, broker_port, 60)

        # 启动订阅线程
        self.sub_thread = threading.Thread(target=self._loop_forever, daemon=True)
        self.sub_thread.start()

        # 启动发布线程（每 2 秒发布一次）
        self.pub_thread = threading.Thread(target=self._publish_loop, daemon=True)
        self.pub_thread.start()

    def on_connect(self, client, userdata, flags, rc, properties):
        my_log.info(f"mqtt订阅错误码连接成功，主进程pid={os.getpid()}")
        client.subscribe("agv/v1/c/auto_test/general/diagnosis/getLastDiagnosicInfo")

    def on_message(self, client, userdata, msg):
        try:
            self.latest_error_code = json.loads(msg.payload.decode())['payload']['errorcodes']
        except Exception as e:
            print(f"解析错误码失败: {e}")

    def _publish_loop(self):
        while True:
            current_time = datetime.fromtimestamp(time.time())
            formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.") + str(current_time.microsecond)[:3] + "Z"
            payload = {
                "method": "getLastDiagnosicInfo",
                "srcAddr": "auto_test",
                "seq": "065db26e-f16f-cb64-9d8f-c784774c59a2",
                "version": "1.0.1",
                "timestamp": formatted_time
            }
            topic = 'agv/v1/s/general/diagnosis/getLastDiagnosicInfo'
            self.client.publish(topic, json.dumps(payload), qos=1)
            time.sleep(2)

    def _loop_forever(self):
        self.client.loop_forever()

    def get_latest_error(self):
        return self.latest_error_code


if __name__ == '__main__':
    error_listener = ErrorCodeSubscriber()


    # 测试主逻辑中实时获取错误码
    for i in range(30):
        print(i)
        error_lst = error_listener.get_latest_error()
        if error_listener.get_latest_error() is None:
            time.sleep(1)
            continue
        advanced_error_lst = [i for i in error_listener.get_latest_error() if i['level'] == 3 or i['level'] == 4]
        # print(advanced_error_lst)
        error_code = [error['errorcode'] for error in advanced_error_lst]
        print(error_code)
        # print(f"[{i}] 当前错误码: {j}")
        time.sleep(1)
    print(f"主进程pid={os.getgid()}")