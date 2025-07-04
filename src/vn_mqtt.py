import json
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import threading
import math

from common.log import my_log

response_event_map = threading.Event()
response_event_reset = threading.Event()
response_event_status = threading.Event()
response_data_map = None
response_data_reset = None
response_data_status = None


def on_connect(client, userdata, flags, rc, properties):
    print("连接成功，订阅切换地图和重定位响应")
    client.subscribe("agv/v1/c/auto_test/3dSlam/localization/switchMap")
    client.subscribe("agv/v1/c/auto_test/general/mainControl/resetLocalization")


def on_message(client, userdata, msg):
    global response_data_map, response_data_reset
    if msg.topic == "agv/v1/c/auto_test/3dSlam/localization/switchMap":
        response_data_map = json.loads(msg.payload.decode())
        response_event_map.set()  # 设置事件，表示已接收到切换地图响应
    elif msg.topic == "agv/v1/c/auto_test/general/mainControl/resetLocalization":
        response_data_reset = json.loads(msg.payload.decode())
        response_event_reset.set()  # 设置事件，表示已接收到重定位响应


# 切换地图函数
def switch_map(map_name):
    global response_data_map
    current_time = datetime.fromtimestamp(time.time())
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.") + str(current_time.microsecond)[:3] + "Z"
    payload = {
        "method": "switchMap",
        "srcAddr": "auto_test",
        "seq": "E1BE73F9-A705-4FA5-A537-2F79248EC85E",
        "timestamp": formatted_time,
        "version": "1.0.1",
        "payload": {"mapName": map_name}
    }
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="auto_test_switch_map")
    client.on_connect = on_connect
    client.on_message = on_message
    response_event_map.clear()  # 清除之前的事件状态
    client.connect("localhost", 1883, 60)
    client.loop_start()
    client.publish("agv/v1/s/3dSlam/localization/switchMap", payload=json.dumps(payload), qos=1)
    response_event_map.wait(timeout=10)  # 超时 10 秒
    client.loop_stop()
    if response_data_map:
        if response_data_map['ack']['code'] == 0:
            my_log.info('切换地图成功')
            return True
        my_log.warning('切换地图失败')
        return None
    else:
        my_log.warning('切换地图获取响应异常')
        return {"error": "No response or timeout"}


# 重置定位函数
def reset_localization(map_name, rl_x, rl_y, rl_yaw):
    global response_data_reset
    current_time = datetime.fromtimestamp(time.time())
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.") + str(current_time.microsecond)[:3] + "Z"
    payload = {
        "timestamp": formatted_time,
        "version": "1.0.1",
        "method": "resetLocalization",
        "srcAddr": "auto_test",
        "seq": "",
        "payload": {
            "isSyncResetService": True,
            "mapName": map_name,
            "seeds": [{
                "pos": {
                    "x": rl_x,
                    "y": rl_y,
                    "z": 0,
                    "roll": 0,
                    "yaw": math.radians(rl_yaw),
                    "pitch": 0
                },
                "error": {
                    "x": 0.1,
                    "y": 0.1,
                    "z": 0.1,
                    "roll": 0.1,
                    "yaw": 0.1,
                    "pitch": 0.1
                }
            }]
        }
    }
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="auto_test_res_loc")
    client.on_connect = on_connect
    client.on_message = on_message
    response_event_reset.clear()  # 清除之前的事件状态
    client.connect("localhost", 1883, 60)
    client.loop_start()
    client.publish("agv/v1/s/general/mainControl/resetLocalization", payload=json.dumps(payload), qos=1)
    response_event_reset.wait(timeout=10)  # 超时 10 秒
    client.loop_stop()
    if response_data_reset:
        if response_data_reset['ack']['code'] == 0:
            my_log.info('重定位成功')
            return True
        my_log.warning('重定位失败')
        return None
    else:
        my_log.warning('重定位获取响应异常')
        return {"error": "No response or timeout"}


def get_localization_status():
    global response_data_status

    def on_connect(client, userdata, flags, rc, properties):
        print("连接成功，订阅 getStatus 响应")
        client.subscribe("agv/v1/c/general/3dSlam/localization/getStatus")

    def on_message(client, userdata, msg):
        global response_data_status
        try:
            response_data_status = json.loads(msg.payload.decode())
            if response_data_status['payload']['mode'] == 0 and response_data_status['payload']['status'] == 2:
                response_event_status.set()
        except Exception as e:
            my_log.warning(f'获取定位状态解析失败：{e}')

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="auto_test_loc_status")
    client.on_connect = on_connect
    client.on_message = on_message
    response_event_status.clear()
    client.connect("localhost", 1883, 60)
    client.loop_start()
    response_event_status.wait(timeout=30)
    client.loop_stop()
    if response_data_status:
        if response_data_status['payload']['mode'] == 0 and response_data_status['payload']['status'] == 2:
            my_log.info('获取定位状态成功')
            return True
        my_log.warning('获取定位状态失败')
        return None
    else:
        my_log.warning('获取定位状态异常')
        return None



if __name__ == "__main__":
    # 调用切换地图函数并获取响应
    # response1 = switch_map("map_20250603174630")
    # print(response1)
    response2 = switch_map("map_20250612163448")
    print(response2)
    response3 = reset_localization('map_20250612163448', 100, 140, 90)
    print(response3)
    response_4 = get_localization_status()
    print(response_4)
