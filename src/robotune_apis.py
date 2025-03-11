# coding=utf-8
import os
import requests
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 从环境变量中读取敏感信息
CLIENT_ID = os.getenv("CLIENT_ID", "afbecef7cd2d37e99b28a46ab1d01f4f")
XSRF_TOKEN = os.getenv("XSRF_TOKEN", "CfDJ8CLpIqq3xxxLjgPMz28yvcIkcamlefVJLtByKCRcVYrCtUzZm_AqTXSiTnvmwWWaMZKLTgWSeeNFkSEpaVQyoo0ROkc0IRcHPPYC0h8svmAL5QxqxoEBgeNbmjBlyhydWV_NcabN1GdL0i_-Zjkm7mg")
ROBOTUNE_USERNAME = os.getenv("ROBOTUNE_USERNAME", "admin")
ROBOTUNE_PASSWORD = os.getenv("ROBOTUNE_PASSWORD", "123qwe")


# 定义API URL
BASE_URL = "http://127.0.0.1:24311/api"
TOKEN_AUTH_URL = f"{BASE_URL}/TokenAuth/Authenticate"
OCCUPY_URL = f"{BASE_URL}/services/sys/TempPermission/Occupy"
DEBUG_FLOW_URL = f"{BASE_URL}/services/task/DynamicFlow/DebugFlow"
UNOCCUPY_URL = f"{BASE_URL}/services/sys/TempPermission/UnOccupy"
DEBUGSTATUS_URL = f"{BASE_URL}/services/task/DynamicFlow/GetDebugStatus?taskId="

class TaskTrigger():
    def __init__(self):   
        self.headers = {
            "accept": "*/*",
            "Authorization": "null",
            'Content-Type': 'application/json-patch+json',
            "X-XSRF-TOKEN": XSRF_TOKEN,
        }
        self.get_authorization()
        self.task_loop_id = '0'
        self.task_loop_normal_exit = False
        self.task_loop_exceptional_exit = False

    def make_request(self, url, data):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"请求过程中发生错误: {e}")
            raise

    def make_request_get(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"请求过程中发生错误: {e}")
            raise        

    # 登录，获取令牌
    def get_authorization(self):
        data = {
            "userNameOrEmailAddress": ROBOTUNE_USERNAME,
            "password": ROBOTUNE_PASSWORD,
            "agvIP": "string",
            "clientId": CLIENT_ID,
            "rememberClient": True
        }

        try:
            response_data = self.make_request(TOKEN_AUTH_URL, data)
            access_token = response_data['result']['accessToken']
            self.headers["Authorization"] = f'Bearer {access_token}'
            logging.info("登录权限，请求成功")
        except KeyError as e:
            logging.error(f"响应体格式错误: {e}")
            raise

    # 获取控制权
    def get_occupy(self):
        data = {
            "clientId": CLIENT_ID,
            "remark": 'auto_test_lgc'
        }
        try:
            response_data = self.make_request(OCCUPY_URL, data)
            if response_data['success']:
                logging.info("成功获取控制权")
            else:
                logging.info("获取控制权失败")
        except Exception as e:
            logging.error(f"获取控制权失败: {e}")

    # 任务流程，下发运行任务。
    # Todo：下发前检查小车是否处于待命状态，如果不是就报警，用例失败 （MQTT） 
    def post_debug_flow(self,taskId,loopNum):
        data = {
            "id": taskId,
            "doCount": loopNum,
            "startTaskGroupIndex": 0,
            "startIndex": 0
        }
        try:
            response_data = self.make_request(DEBUG_FLOW_URL, data)
            print(response_data)
            # 检查是否有task_loop_id ，没有的话需要返回失败，下发任务失败就要去执行下一个任务。
            if response_data['success']:
                self.task_loop_id = response_data['result']
                logging.info("成功下发运行任务")
            else:
                print("检查是否有task_loop_id",response_data['error'])

            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except Exception as e:
            logging.error(f"下发运行任务失败: {e}")
            self.task_loop_id = '0'

    def get_DebugStatus(self):
        try:
            response_data = self.make_request_get(DEBUGSTATUS_URL+str(self.task_loop_id))
            if response_data['result']['status']['finish'] == True:
                self.task_loop_normal_exit = True
            if response_data['result']['status']['taskStatus'] == 'paused':
                self.task_loop_exceptional_exit = True

            #任务流程状态 {'taskStatus': 'completed', 'taskPercent': 100, 'finish': True}

            # 关注被暂停的状态，这种被认为异常退出。
            # 任务流程状态 {'taskStatus': 'canceled', 'taskPercent': 100, 'finish': True}

            # 遇到了异常的话，就会处于被暂停的状态。
            # 任务流程状态 {'taskStatus': 'paused', 'taskPercent': 10, 'finish': False}

            logging.info("成功查询动态任务流程状态",response_data['result']['status'])

        except Exception as e:
            logging.error(f"查询动态任务流程状态失败: {e}")

# {'result': {'taskId': '1e5d3570-1048-46ec-9862-836f2614fc47', 'repeatCount': 20, 'repeatIndex': 1, 
#             'taskCount': 2, 'taskIndex': 0, 'keyTaskIndex': 1, 'flowName': '密闭空间穿梭AT',
#               'flowId': 67, 'schemeId': 1, 'logicTaskId': 559, 'isKeyTask': False, 'groupSorting': 0,
#                 'information': None, 'innerTaskId': '486963F1-EF93-48F6-B909-7CA50BA8ECF1',
#                 'status': {'taskStatus': 'canceled', 'taskPercent': 100, 'finish': True}, 
#                   'agvTask': {'id': 48, 'name': 'CommonMove', 'displayName': '通用移动', 
#                               'taskType': {'id': 2, 'name': 'MoveTo', 'displayName': '移动', 
#                                            'requiredPark': False}, 'districtId': 67}, 
#                                            'taskGroup': {'groupId': 189, 'groupName': '默认任务组'}, 
#                                            'parkNumber': None, 
#     'fullPathIds': [13415, 13397, 13327, 13451, 13368, 13367, 13374, 13354, 13083, 13052, 13071, 13075, 13040, 13031, 13018, 13025, 13095, 13090, 13093, 13230, 13191, 13196, 13231, 13226, 13085, 13114, 13129, 13099, 13062, 13066, 13077, 13059, 13063, 13068, 13240, 13109, 13108, 13134, 13265, 13212, 13211, 13206, 13233, 13096, 13423, 13437, 13412, 13443, 13441, 13418, 13431, 13390, 13404, 13439, 13442, 13422, 13116, 13246, 13245, 13208, 13232, 13210, 13107, 13465, 13533, 13473, 13469, 13506, 13507, 13453, 13479, 13537, 13644, 13645, 13646, 13648, 13649, 13651, 13485, 13483, 13514, 13515, 13457, 13491, 13543, 13544, 13673, 13674, 13675, 13676, 13677, 13545, 13497, 13495, 13529, 13530, 13531, 13463, 13555, 13556, 13693, 13694, 13615, 13714], 'endCoordinates': '75.692,-68.102', 'startCoordinates': '-3.674,2.387', 'sourceSys': 'robotune'},
#   'targetUrl': None, 'success': True, 'error': None, 'unAuthorizedRequest': False, '__abp': True}



    # 释放控制权
    def get_unoccupy(self):
        data = {}
        try:
            self.make_request(UNOCCUPY_URL, data)
            logging.info("释放控制权")
        except Exception as e:
            logging.error(f"释放控制权失败: {e}")


GetAllServiceInstance_URL = f"{BASE_URL}/services/pm/ServiceInstance/GetAllServiceInstance"
StopInstance_URL = f"{BASE_URL}/services/pm/ServiceInstance/StopInstance"
StartInstance_URL = f"{BASE_URL}/services/pm/ServiceInstance/StartInstance"

class AGVsysTrigger():
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "Authorization": "null",
            'Content-Type': 'application/json-patch+json',
            "X-XSRF-TOKEN": XSRF_TOKEN,
        }
        self.ServiceInstanceList=[]
        self.GetAllServiceInstance()

    def make_request(self, url, data):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"请求过程中发生错误: {e}")
            raise

    def make_request_get(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"请求过程中发生错误: {e}")
            raise        

    def GetAllServiceInstance(self):
        try:
            response_data = self.make_request_get(GetAllServiceInstance_URL)
            if response_data['success']:
                self.ServiceInstanceList = response_data['result']['data']
            else:
                print(response_data['error'])
            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except Exception as e:
            logging.error(f"下发运行任务失败: {e}")
            self.task_loop_id = '0'
        
        pass

    def StartInstance(self,ServiceInstanceId):
        try:
            data = {
                "Id": ServiceInstanceId
            }
            response_data = self.make_request(StartInstance_URL, data)
            print(response_data)
            if response_data['success']:
                logging.info("成功启动AGV程序")
        except Exception as e:
            logging.error(f"开始AGV服务模块异常: {e}")

    def StopInstance(self, ServiceInstanceId):
        try:
            if ServiceInstanceId:
                data = {
                    "Id": ServiceInstanceId
                }
                response_data = self.make_request(StopInstance_URL, data)
                print(response_data)
        except Exception as e:
            logging.error(f"停止AGV服务模块异常: {e}")  
                        
    def StopALLInstance(self):
        for data in self.ServiceInstanceList:
            self.StopInstance(data['id'])

    def StartALLInstance(self):
        # 先找到ServiceInstanceList中 感知服务的 ID
        for data in self.ServiceInstanceList:
            if data['serviceType']['serviceTypeName'] == '3DSlamPrinter':
                self.StartInstance(data['id'])        
        for data in self.ServiceInstanceList:
            if data['serviceType']['serviceTypeName'] == 'perception':
                self.StartInstance(data['id'])
        for data in self.ServiceInstanceList:
            if data['serviceType']['serviceTypeName'] == 'general':
                self.StartInstance(data['id'])
        for data in self.ServiceInstanceList:
            if data['serviceType']['serviceTypeName'] == '3DSlam':
                self.StartInstance(data['id'])      
    
    # todo-启动前确认地图和agv初始位置。根据webots的初始位姿态来处理？好像也不错。或者根据任务里面的移动任务的起点来处理。

if __name__ == "__main__":

    # a = AGVsysTrigger()
    # a.StopALLInstance()
    # exit()

    try:
        taskId = 67  # 示例 taskid
        loopNum = 1  # 示例 loopnum        
        task_trigger = TaskTrigger()
        task_trigger.get_occupy()
        task_trigger.post_debug_flow(taskId,loopNum)    
        task_trigger.get_unoccupy()
    except Exception as e:
        logging.error(f"程序执行过程中发生错误: {e}")