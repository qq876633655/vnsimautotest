# coding=utf-8
import datetime
import signal
import psutil
import requests
import logging
from robotune_apis import *
import subprocess
import time
import csv
import math
import os
import logging
import shutil
from pathlib import Path
import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber

import proto_messages.pose_pb2 as pose_pb2

import sys


# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义路径常量ecal_core
LOG_SOURCE_DIR = Path('/home/visionnav/log')
LOG_TARGET_BASE_DIR = Path('/home/visionnav/autotest')
CPU_CSV_DIR = Path('/home/visionnav/VNSim/luoguancong/csv')
FLAG_received = False

# 监听svc/pose话题，如果有消息了，则退出循环
def wait_for_pose_topic():


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

# 获取任务流程列表
def get_DynamicFlow_GetAll():

    url = (
        "http://127.0.0.1:24311/api/services/task/DynamicFlow/GetAll?MaxResultCount=100"
    )

    try:
        # 发送POST请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            print("成功获取任务流程列表")
            task_list = response.json()['result']['items']
            return task_list
            # print(task_list)
            # for i in task_list:
            #     # 提取关键词AT的任务作为循环任务 , 后续可能要分类，哪些测感知哪些测定位
            #     if 'AT' in i['name']:
            #         print(i['name'])
            #         print(i['id'])
            #         get_FlowInfo(i['id'])


        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("错误信息:", response.text)

    except Exception as e:
        print(f"请求过程中发生错误: {e}")


# 测试启动wbt文件接口
def webots_start_wbt(wbt_file_name,spawn_point):
    url = "http://127.0.0.1:5000/start_wbt"
    data = {
        "filename": wbt_file_name,
        "flag_start_with_bright_eye": False,
        "spawn_point": spawn_point
    }
    print(data)
    #         "file_path": "/home/visionnav/vn_wbt_project/密闭空间/worlds/密闭空间.wbt",
    response = requests.post(url, json=data)
    print(response.json())

# 测试强制停止wbt文件接口
def webots_stop_force():
    url = "http://127.0.0.1:5000/stop_force"
    response = requests.post(url)
    print(response.json())

def handle_slam_map_and_spawn_point(spawn_point,locationName):
    # 验证 spawn_point 参数
    if not isinstance(spawn_point, list) or len(spawn_point) != 3:
        logging.error("Invalid spawn_point format: expected a list of length 3")
        return

    # 获取配置的路径
    folder_path = os.getenv('SLAM_SPAWN_POINT_PATH', '/home/visionnav/AGVServices/3dSlam/lastagvpose')

    try:
        if os.path.exists(folder_path):
            logging.info(f"Folder {folder_path} exists, modifying its content.")
            # 将 spawn_point 的内容写入文件，agvpose1.csv 
            with open(os.path.join(folder_path, 'agvpose1.csv'), 'w') as file:
                file.write(f"{spawn_point[0]} {spawn_point[1]} 0 {spawn_point[2]* math.pi / 180} 0 0\n")
                # file.write(f"{spawn_point[0]} {spawn_point[1]} 0 3.1415 0 0\n")

                # file.write(f"{spawn_point[0]} {spawn_point[1]} 0 0 0 0\n")
            with open(os.path.join(folder_path, 'agvpose2.csv'), 'w') as file:
                file.write(f"{spawn_point[0]} {spawn_point[1]} 0 {spawn_point[2]* math.pi / 180} 0 0\n")
                # file.write(f"{spawn_point[0]} {spawn_point[1]} 0 0 0 0\n")
            with open(os.path.join(folder_path, 'mappath.txt'), 'w') as file:
                file.write(f"{'/home/visionnav/AGVServices/3dSlam/map'+'/'+locationName+','}\n")
        else:
            # 如果文件夹不存在，则创建
            os.makedirs(folder_path, exist_ok=True)
            with open(os.path.join(folder_path, 'agvpose1.csv'), 'w') as file:
                file.write(f"{spawn_point[0]} {spawn_point[1]} 0 {spawn_point[2]* math.pi / 180} 0 0\n")
            with open(os.path.join(folder_path, 'agvpose2.csv'), 'w') as file:
                file.write(f"{spawn_point[0]} {spawn_point[1]} 0 {spawn_point[2]* math.pi / 180} 0 0\n")
            with open(os.path.join(folder_path, 'mappath.txt'), 'w') as file:
                file.write(f"{folder_path+'/'+locationName}\n")            
            logging.info(f"Created folder {folder_path}.")
    except Exception as e:
        logging.error(f"Error handling folder {folder_path}: {e}")


class FlowInfoParser:
    def __init__(self,task_id):
        self.task_id = task_id
        self.Spawn_point = None
        self.get_FlowInfo()
        self.wbt_file_name = None
        self.get_DynamicFlow_GetDistrict()
        self.map_id = None
        self.get_DynamicFlow_GetDistrict()
        self.locationName = None
        self.get_map_District()
        # print(self.Spawn_point,self.wbt_file_name,self.map_id,self.locationName,self.task_id)


    def get_FlowInfo(self):
        url = ("http://127.0.0.1:24311/api/services/task/DynamicFlow/GetFlowInfo?Id="+str(self.task_id))

        try:
            # 发送POST请求
            response = requests.get(url)
            
            # 检查响应状态码
            if response.status_code == 200:
                print("成功获取任务流程列表")
                FlowInfo = response.json()

                # 获取第一个通用移动的顶点为slam以及wbt的“出生点”坐标
                for i in FlowInfo['result']['taskGroups']:
                    # 组内子任务循环
                    for j in i['taskTpls']:
                        if j['agvTaskDisplayName'] == '通用移动':
                            self.Spawn_point = j['vertexList']
                            print('通用移动',j['vertexList'],type(j['vertexList']))
                            self.districtId = j['districtId']
                            print('通用移动',j['districtId'],type(j['districtId']))
                            break

                # 获取通用等待的个数和ID
                # 分组循环
                for i in FlowInfo['result']['taskGroups']:
                    # 组内子任务循环
                    for j in i['taskTpls']:
                        print(j['agvTaskDisplayName'])
                        if '通用等待' in  j['agvTaskDisplayName']:
                            print(j['id'])
            else:
                print(f"请求失败，状态码：{response.status_code}")
                print("错误信息:", response.text)

        except Exception as e:
            print(f"请求过程中发生错误: {e}")    

    def get_DynamicFlow_GetDistrict(self):
        url = ("http://127.0.0.1:24311/api/services/task/DynamicFlow/GetDistrict?districtId="+str(self.districtId))

        try:
            # 发送POST请求
            response = requests.get(url)
            
            # 检查响应状态码
            if response.status_code == 200:
                result = response.json()
                # 获取分区名称，对应就是wbt的名称
                self.wbt_file_name = result['result']['name']
                self.map_id = result['result']['mapId']

            else:
                print(f"请求失败，状态码：{response.status_code}")
                print("错误信息:", response.text)

        except Exception as e:
            print(f"请求过程中发生错误: {e}")      

    def get_map_District(self):
        url = ("http://127.0.0.1:24311/api/services/map/District/Get?Id="+str(self.districtId))
        try:
            # 发送POST请求
            response = requests.get(url)
            
            # 检查响应状态码
            if response.status_code == 200:
                result = response.json()

                # 获取slam地图的名称，便于定位
                self.locationName = result['result']['locationName']

            else:
                print(f"请求失败，状态码：{response.status_code}")
                print("错误信息:", response.text)

        except Exception as e:
            print(f"请求过程中发生错误: {e}")      

# class LogManege:
#     def __init__(self,task_id):
#         self.task_id = task_id
#         self.get_Log_GetLog()

def clear_agv_log():
    os.system("rm -rf /home/visionnav/log")

    try:
        if os.path.exists(LOG_SOURCE_DIR):
            shutil.rmtree(LOG_SOURCE_DIR)
            logging.info(f"成功删除日志目录: {LOG_SOURCE_DIR}")
        else:
            logging.warning(f"日志目录不存在: {LOG_SOURCE_DIR}")
    except Exception as e:
        logging.error(f"删除日志目录失败: {LOG_SOURCE_DIR}, 错误信息: {e}")
def log_dir(task_name,task_id):
    return LOG_TARGET_BASE_DIR / f"{task_name}_{task_id}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
def save_agv_log(task_name,task_id):
    # try:
    #     # 生成保存日志的日期
    #     # 安全地拼接路径
    #     save_log_path = LOG_TARGET_BASE_DIR / f"{task_name}_{task_id}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        
    #     # 记录日志
    #     logging.info(f"Saving log to {save_log_path}")

    #     # 复制日志目录
    #     print("复制AGV目录")
    #     shutil.copytree(LOG_SOURCE_DIR, save_log_path)
    #     time.sleep(2)
    #     print("复制CPU目录")
    #     shutil.copytree(CPU_CSV_DIR, save_log_path)
    try:
        # 安全地拼接路径
        save_log_path = log_dir(task_name,task_id)
        # 记录日志
        logging.info(f"Saving log to {save_log_path}")
        shutil.copytree(LOG_SOURCE_DIR, os.path.join(save_log_path, os.path.basename(LOG_SOURCE_DIR)))
        print(f"成功复制 {LOG_SOURCE_DIR} 到 {save_log_path}")
        shutil.copytree(CPU_CSV_DIR, os.path.join(save_log_path, os.path.basename(CPU_CSV_DIR)))
        print(f"成功复制 {CPU_CSV_DIR} 到 {save_log_path}")

    except FileExistsError:
        print("目标目录中已有同名文件夹，请检查。")
    except Exception as e:
        print(f"发生错误: {e}")

        


    except FileExistsError:
        logging.error(f"Directory {save_log_path} already exists.")
    except PermissionError:
        logging.error("Permission denied when trying to copy logs.")
    except Exception as e:
        logging.error(f"An error occurred while saving logs: {e}")

# 时间戳转格式化时间
def timestamp_to_formatted_time(timestamp):
    error_sec = timestamp // 1000
    error_ms = timestamp % 1000
    dt_object = datetime.datetime.fromtimestamp(error_sec)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return f"{formatted_time}.{error_ms:03d}"


# 获取robotune异常情况
def robotune_error_code_get(task_name,task_id):
    save_log_path = log_dir(task_name,task_id)
    error_list = []
    if not error_list:
        for i in range(3, 5):
            try:
                response = requests.get(f"http://127.0.0.1:24311/api/services/pm/WarningRecord/GetAll?Level={i}")
                response.raise_for_status()  # 检查请求是否成功
                items = response.json()["result"]["items"]
                for j in items:
                    if 0 < (int(time.time() * 1000) - j["startTimestamp"]) / 1000 < 10:
                        error_time = timestamp_to_formatted_time(j['startTimestamp'])
                        error_info = f"时间：{error_time} 错误码：{j['errorCode']} 错误信息：{j['warning']['name']} 错误等级：{j['level']} 错误模块：{j['serviceType']['serviceTypeName_zh']}"
                        error_list.append(error_info)
            except requests.RequestException as e:
                print(f"请求发生错误: {e}")
            except (KeyError, IndexError) as e:
                print(f"解析响应数据时发生错误: {e}")

    with open(f'{save_log_path}/robotune_error.txt', 'w', encoding='utf-8') as f:
        for item in error_list:
            f.write(f"{item}\n")
    f.close()

if __name__ == "__main__":



    # 获取用例任务列表
    task_list = get_DynamicFlow_GetAll()
    task_report = []
    
    

    for i in task_list:
        # 提取关键词AT的任务作为循环任务 , 后续可能要分类，哪些测感知哪些测定位。输出用例报告，通过用例的精度、异常用例的失败原因。
        if '单自动门DW' in i['name']:
            clear_robotune_task()
            print(i['name'],i['id'])
            # get_FlowInfo(i['id'])test
            webots_stop_force()
            agv = AGVsysTrigger()
            agv.StopALLInstance()

            # 启动对应的wbt场景，并且等待准备好slam的相关数据。需要等待wbt启动后，再启动agv程序
            FIP = FlowInfoParser(i['id'])
            spawn_point_float_list = [float(x) for x in FIP.Spawn_point[0].split(',')]
            handle_slam_map_and_spawn_point(spawn_point_float_list,FIP.locationName)

            # 启动wbt
            webots_start_wbt(FIP.wbt_file_name,spawn_point_float_list)

            clear_agv_log()
            time.sleep(15)


            # 如果程序没有正常启动，则启动所有实例。
            agv.StartALLInstance()
            

            # 监听svc/pose话题，如果有消息了，则退出循环。证明仿真程序启动成功。Todo:可以加上超时检测。
            wait_for_pose_topic()
            # time.sleep(30)


   
            try:
                print("开始下发任务")
                taskId = i['id']  # 示例 taskid
                print(taskId)
                loopNum = 1  # 设置循环次数，默认20次 
                task_trigger = TaskTrigger()
                task_trigger.get_occupy()
                task_trigger.post_debug_flow(taskId,loopNum)    
                task_trigger.get_unoccupy()
                # 如果没有成功生成任务ID就是失败了，可能是路径规划问题、可能是地图问题、可能是车辆待机问题
                if task_trigger.task_loop_id == '0':
                    logging.error(f"下发任务失败，该用例失败")
                    webots_stop_force()
                    agv.StopALLInstance()
                    save_agv_log(i['name'],i['id'])
                    time.sleep(15)
                    task_report.append([i['name'],i['id'],'下发任务失败'])
                    # save_agv_log(i['name'],i['id'])
                    continue

            except Exception as e:
                logging.error(f"程序执行过程中发生错误: {e}")


            # 过程监控，记录使用，是否有异常，如果有异常就复制一份日志.并且循环等待。        
            # # 用子线程调用脚本来copy文件

            # 获取当前路径
            process_record = subprocess.Popen(['python3', '/home/visionnav/VNSim/luoguancong/vnsimautotest/src/robotune_nav_recoder.py'])

            # 记录各线程的CPU和内存信息
            process_csv = subprocess.Popen(['python3', '/home/visionnav/VNSim/luoguancong/vnsimautotest/src/process_csv_linux.py'])
            
            # loop waitting for task finish
            while True:
                # 获取任务状态
                # task_status = task_trigger.get_task_status(taskId)
                task_trigger.get_DebugStatus()

                if task_trigger.task_loop_normal_exit:
                    # 正常退出，清空日志
                    # Todo：增加数据分析模块，重复精度不合格也要判断为用例失败
                    process_record.terminate()
                    # 杀死cpu占用运行的进程
                    process_csv.kill()
                    webots_stop_force()
                    # 保存日志
                    agv.StopALLInstance()
                    save_agv_log(i['name'],i['id'])
                    time.sleep(5)
                    print('正常退出')
                    task_report.append([i['name'],'用例执行通过'])
                    # save_agv_log(i['name'],i['id'])                    
                    break
                if task_trigger.task_loop_exceptional_exit:
                    # 异常退出，保留日志，获取一下对应的
                    process_record.terminate()
                    # 杀死cpu占用运行的进程
                    process_csv.kill()
                    # 清除當前任务流程
                    clear_robotune_task()
                    # 关闭仿真环境和AGV程序
                    webots_stop_force()
                    agv.StopALLInstance()
                    # 保存日志和csv
                    save_agv_log(i['name'],i['id'])
                    # 保存异常流程的错误信息
                    robotune_error_code_get(i['name'],i['id'])
                    time.sleep(5)
                    print('异常退出')
                    task_report.append([i['name'],'用例失败,执行时异常'])
                    # save_agv_log(i['name'],i['id'])
                    break
                else:
                    # 循环等待
                    time.sleep(1)

    
    print(task_report)
    print(f"执行测试数量:{len(task_report)}")
    logging.info("Task Report: %s", task_report)