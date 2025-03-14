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
from threading import Event
FLAG_received = False

def wait_for_pose_topic():

    # 监听svc/pose话题，如果有消息了，则退出循环

    global FLAG_received 

    # 初始化eCAL
    ecal_core.initialize(sys.argv, "Simple Topic Waiter")
    
    # 创建订阅者
    sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
    
    # 定义回调函数
    def callback(topic_name, msg, time):
        print(f"收到 {msg} 的首条消息")
        global FLAG_received 
        FLAG_received = True  # 修改状态
        sub.rem_callback(callback)
        ecal_core.shutdown_core()

    # 设置回调
    sub.set_callback(callback)
    
    # 等待循环
    print(f"等待话题 [svc/pose]...")
    while not FLAG_received:
        print("正在等待...")
        time.sleep(1)
    print("话题 [svc/pose] 已收到消息，退出循环")
    return


if __name__ == "__main__":

    wait_for_pose_topic()


