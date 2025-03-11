# coding=utf-8
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


# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义路径常量
LOG_SOURCE_DIR = Path('/home/visionnav/log')
LOG_TARGET_BASE_DIR = Path('/home/visionnav/autotest')

# 获取任务流程列表
def get_DynamicFlow_GetAll():

    url = (
        "http://127.0.0.1:24311/api/services/task/DynamicFlow/GetAll"
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

def save_agv_log(task_name,task_id):
    try:
        # 安全地拼接路径
        save_log_path = LOG_TARGET_BASE_DIR / f"{task_name}_{task_id}"
        
        # 记录日志
        logging.info(f"Saving log to {save_log_path}")
        
        # 复制日志目录
        shutil.copytree(LOG_SOURCE_DIR, save_log_path)
        
    except FileExistsError:
        logging.error(f"Directory {save_log_path} already exists.")
    except PermissionError:
        logging.error("Permission denied when trying to copy logs.")
    except Exception as e:
        logging.error(f"An error occurred while saving logs: {e}")


if __name__ == "__main__":

    # 获取用例任务列表
    task_list = get_DynamicFlow_GetAll()

    task_report = []
    

    for i in task_list:

        # 提取关键词AT的任务作为循环任务 , 后续可能要分类，哪些测感知哪些测定位。输出用例报告，通过用例的精度、异常用例的失败原因。
        if 'YD' in i['name']:
            print(i['name'],i['id'])
            # get_FlowInfo(i['id'])
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

            
            time.sleep(30)



            try:
                print("开始下发任务")
                taskId = i['id']  # 示例 taskid
                loopNum = 1  # 循环次数，默认20次 
                task_trigger = TaskTrigger()
                task_trigger.get_occupy()
                task_trigger.post_debug_flow(taskId,loopNum)    
                task_trigger.get_unoccupy()
                # 如果没有成功生成任务ID就是失败了，可能是路径规划问题、可能是地图问题、可能是车辆待机问题
                if task_trigger.task_loop_id == '0':
                    logging.error(f"下发任务失败，该用例失败")
                    webots_stop_force()
                    agv.StopALLInstance()
                    time.sleep(15)
                    task_report.append([i['name'],i['id'],'下发任务失败'])
                    save_agv_log(i['name'],i['id'])
                    continue    

            except Exception as e:
                logging.error(f"程序执行过程中发生错误: {e}")


            # 过程监控，记录使用，是否有异常，如果有异常就复制一份日志.并且循环等待。        
            # # 用子线程调用脚本来copy文件

            # 获取当前路径
            process_record = subprocess.Popen(['python3', '/home/visionnav/VNSim/luoguancong/python_ecal/src/robotune_nav_recoder.py'])

            # loop waitting for task finish
            while True:
                # 获取任务状态
                # task_status = task_trigger.get_task_status(taskId)
                task_trigger.get_DebugStatus()

                if task_trigger.task_loop_normal_exit:
                    # 正常退出，清空日志
                    # Todo：增加数据分析模块，重复精度不合格也要判断为用例失败
                    process_record.terminate()
                    webots_stop_force()
                    agv.StopALLInstance()
                    time.sleep(15)
                    print('正常退出')
                    task_report.append([i['name'],'用例执行通过'])
                    save_agv_log(i['name'],i['id'])                    
                    break
                if task_trigger.task_loop_exceptional_exit:
                    # 异常退出，保留日志，获取一下对应的
                    process_record.terminate()
                    # 关闭仿真环境和AGV程序
                    webots_stop_force()
                    agv.StopALLInstance()
                    time.sleep(15)
                    print('异常退出')
                    task_report.append([i['name'],'用例失败,执行时异常'])
                    save_agv_log(i['name'],i['id'])
                    break
                else:
                    # 循环等待
                    time.sleep(1)


    print(task_report)
    logging.info("Task Report: %s", task_report)