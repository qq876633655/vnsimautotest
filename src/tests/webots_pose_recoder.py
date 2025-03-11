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
import proto_messages.transfer_pb2 as transfer_pb2


# 回调函数，处理接收到的消息
def on_message(topic_name, msg, msg_time):
    global messages_buffer
    global FLAG_RECODE
    row_list = []
    if not FLAG_RECODE:
        return

    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    # siyuanshu 2 theta    
    row_list.extend([current_time, round(msg.position.x, 4), round(msg.position.y, 4), round(msg.position.z, 4)])

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

    url_GetCurrentTaskInfo = (
        "http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo"
    )
    reponse_GetCurrentTaskInfo = requests.get(url_GetCurrentTaskInfo, headers=headers)
    result_GetCurrentTaskInfo = reponse_GetCurrentTaskInfo.json()
    print("task name = ", result_GetCurrentTaskInfo["result"]["taskId"])
    row_list.extend(result_GetCurrentTaskInfo["result"]["taskId"])

    messages_buffer.append(row_list)

    FLAG_RECODE = False


if __name__ == "__main__":

    # 触发信号

    print("监听记录信号：执行等待任务中时记录信息")
    interval_time = 2
    taskName = ""

    ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")

    # 创建消息缓冲区
    messages_buffer = []

    # 创建并启动写入文件的线程
    write_thread = threading.Thread(target=write_to_file, daemon=True)
    write_thread.start()

    sub = ProtoSubscriber("webot/transfer", transfer_pb2.MTransfer)
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
