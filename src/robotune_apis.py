# -*- coding: utf-8 -*-

import os
import time
import requests
import json

from duplicity.globals import backup_name

from src.log import my_log


# 从环境变量中读取敏感信息
CLIENT_ID = os.getenv("CLIENT_ID", "afbecef7cd2d37e99b28a46ab1d01f4f")
XSRF_TOKEN = os.getenv("XSRF_TOKEN",
                       "CfDJ8CLpIqq3xxxLjgPMz28yvcIkcamlefVJLtByKCRcVYrCtUzZm_AqTXSiTnvmwWWaMZKLTgWSeeNFkSEpaVQyoo0ROkc"
                       "0IRcHPPYC0h8svmAL5QxqxoEBgeNbmjBlyhydWV_NcabN1GdL0i_-Zjkm7mg")
ROBOTUNE_USERNAME = os.getenv("ROBOTUNE_USERNAME", "admin")
ROBOTUNE_PASSWORD = os.getenv("ROBOTUNE_PASSWORD", "123qwe")

# 定义API URL
BASE_URL = "http://127.0.0.1:24311/"
# 登录、获取控制权、释放控制权
Authenticate_URL = f"{BASE_URL}/api/TokenAuth/Authenticate"
Occupy_URL = f"{BASE_URL}/api/services/sys/TempPermission/Occupy"
UnOccupy_URL = f"{BASE_URL}/api/services/sys/TempPermission/UnOccupy"
# 备份获取、备份恢复
Backup_GetAll_URL = f"{BASE_URL}/api/services/sys/Backup/GetAll"
Backup_Recovery_URL = f"{BASE_URL}/api/services/sys/Backup/Recovery"
# 所有服务获取、停止服务、启动服务
GetAllServiceInstance_URL = f"{BASE_URL}/api/services/pm/ServiceInstance/GetAllServiceInstance"
StopInstance_URL = f"{BASE_URL}/api/services/pm/ServiceInstance/StopInstance"
StartInstance_URL = f"{BASE_URL}/api/services/pm/ServiceInstance/StartInstance"
# 分区信息、地图信息
GetDistrict_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetDistrict"
District_Get_URL = f"{BASE_URL}/api/services/map/District/Get"
# 清除任务缓存、任务执行、任务状态、任务详情、正在执行中的任务
ClearExistTask_URL = f"{BASE_URL}/api/services/task/DynamicFlow/ClearExistTask"
DebugFlow_URL = f"{BASE_URL}/api/services/task/DynamicFlow/DebugFlow"
GetDebugStatus_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetDebugStatus?taskId=" # 参数放函数内
GetFlowInfo_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetFlowInfo"
GetCurrentTaskInfo_URL = f"{BASE_URL}/api/services/task/Agv/GetCurrentTaskInfo"
# 通参一级节点获取、通参二级及以下参数获取
GetAllNodes_URL = f"{BASE_URL}/api/services/pm/CommonParamter/GetAllNodes"
GetRootNodes_URL = f"{BASE_URL}/api/services/pm/CommonParamter/GetRootNodes"
# 错误码获取、终止、复位启动
WarningRecord_GetAll_URL = f"{BASE_URL}/api/services/pm/WarningRecord/GetAll"
CtrlTaskStatus_URL = f"{BASE_URL}/api/services/task/Agv/CtrlTaskStatus"
SetCtrlButton_URL = f"{BASE_URL}/api/services/task/SetCtrlButton"
# 自动回归
AutoBackTask_CreateTask_URL = f"{BASE_URL}/api/services/task/AutoBackTask/CreateTask"


class Auth:
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

    def request_post(self, url, data):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            if response.status_code != 200:
                # print(response.json()['error'])
                print(response.json()['error']['message'])
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            my_log.error(f"请求过程中发生错误: {e}")
            raise

    def request_get(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            my_log.error(f"请求过程中发生错误: {e}")
            raise

    def request_delete(self, url):
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()

        except requests.exceptions.RequestException as e:
            my_log.error(f"请求过程中发生错误: {e}")
            raise

    def get_authorization(self):
        data = {
            "userNameOrEmailAddress": ROBOTUNE_USERNAME,
            "password": ROBOTUNE_PASSWORD,
            "agvIP": "string",
            "clientId": CLIENT_ID,
            "rememberClient": True
        }
        try:
            response_data = self.request_post(Authenticate_URL, data)
            access_token = response_data['result']['accessToken']
            self.headers["Authorization"] = f'Bearer {access_token}'
            my_log.info("登录权限，请求成功")
        except KeyError as e:
            my_log.error(f"响应体格式错误: {e}")
            raise

    def get_occupy(self):
        data = {
            "clientId": CLIENT_ID,
            "remark": 'auto_test_lgc'
        }
        try:
            response_data = self.request_post(Occupy_URL, data)
            if response_data['success']:
                my_log.info("成功获取控制权")
            else:
                my_log.info("获取控制权失败")
        except Exception as e:
            my_log.error(f"获取控制权失败: {e}")

    def get_unoccupy(self):
        data = {}
        try:
            self.request_post(UnOccupy_URL, data)
            my_log.info("释放控制权")
        except Exception as e:
            my_log.error(f"释放控制权失败: {e}")

    # 任务流程，下发运行任务。
    # Todo：下发前检查小车是否处于待命状态，如果不是就报警，用例失败 （MQTT） 
    def post_debug_flow(self, taskId, loopNum):
        data = {
            "id": taskId,
            "doCount": loopNum,
            "startTaskGroupIndex": 0,  # 单步任务在任务列表中的组索引
            "startIndex": 0  # 单步任务在任务列表中的单个索引
        }
        try:
            # wait ten seconds to robotune is ready
            time.sleep(20)
            response_data = self.make_request(DEBUG_FLOW_URL, data)
            print(response_data)
            # 检查是否有task_loop_id ，没有的话需要返回失败，下发任务失败就要去执行下一个任务。
            if response_data['success']:
                self.task_loop_id = response_data['result']
                my_log.info("成功下发运行任务")
                return response_data
            else:
                print("检查是否有task_loop_id", response_data['error'])

            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except Exception as e:
            my_log.error(f"下发运行任务失败: {e}")
            self.task_loop_id = '0'

    def get_DebugStatus(self):
        try:
            response_data = self.make_request_get(DEBUGSTATUS_URL + str(self.task_loop_id))
            if response_data['result']['status']['finish'] == True:
                self.task_loop_normal_exit = True
            if response_data['result']['status']['taskStatus'] == 'paused':
                self.task_loop_exceptional_exit = True

            # 任务流程状态 {'taskStatus': 'completed', 'taskPercent': 100, 'finish': True}

            # 关注被暂停的状态，这种被认为异常退出。
            # 任务流程状态 {'taskStatus': 'canceled', 'taskPercent': 100, 'finish': True}

            # 遇到了异常的话，就会处于被暂停的状态。
            # 任务流程状态 {'taskStatus': 'paused', 'taskPercent': 10, 'finish': False}

            # my_log.info("成功查询动态任务流程状态",response_data['result']['status'])

        except Exception as e:
            my_log.error(f"查询动态任务流程状态失败: {e}")

class ServiceTrigger(Auth):
    def __init__(self):
        super().__init__()
        self.service_instance_lst = []
        self.get_all_service_instance()

    def get_all_service_instance(self):
        try:
            response_data = self.request_get(GetAllServiceInstance_URL)
            if response_data['success']:
                self.service_instance_lst = response_data['result']['data']
            else:
                my_log.error(response_data['error'])
            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except Exception as e:
            my_log.error(f"下发运行任务失败: {e}")
            self.task_loop_id = '0' # 当前运行任务id？？

    def start_instance(self, service_id):
        try:
            data = {"Id": service_id}
            response_data = self.request_post(StartInstance_URL, data)
            if response_data['success']:
                my_log.info(f"成功启动AGV程序：{service_id}")
        except Exception as e:
            my_log.error(f"开始AGV服务模块异常: {e}")

    def stop_instance(self, service_id):
        try:
            data = {
                "Id": service_id
            }
            response_data = self.request_post(StopInstance_URL, data)
            if response_data['success']:
                my_log.info(f"成功停止AGV程序：{service_id}")
        except Exception as e:
            my_log.error(f"停止AGV服务模块异常: {e}")

    def start_all_instance(self):
        # 先找到ServiceInstanceList中 感知服务的 ID
        for data in self.service_instance_lst:
            if data['serviceType']['serviceTypeName'] == '3DSlamPrinter':
                self.start_instance(data['id'])
        for data in self.service_instance_lst:
            if data['serviceType']['serviceTypeName'] == 'perception':
                self.start_instance(data['id'])
        for data in self.service_instance_lst:
            if data['serviceType']['serviceTypeName'] == 'general':
                self.start_instance(data['id'])
        for data in self.service_instance_lst:
            if data['serviceType']['serviceTypeName'] == '3DSlam':
                self.start_instance(data['id'])

    def stop_all_instance(self):
        for data in self.service_instance_lst:
            self.stop_instance(data['id'])

    def service_status(self, service_id):
        """
        获取服务状态K
        :param service_id:
        :return:
        """
        pass




class RobotuneInstance(Auth):
    def __init__(self):
        super().__init__()
        self.backup_lst = []

    def backup_get_all(self, max_result_count=100, page_index=1):
        try:
            get_all_url = Backup_GetAll_URL + f"?MaxResults={max_result_count}&PageIndex={page_index}"
            response_data = self.request_get(get_all_url)
            self.backup_lst = response_data['result']['items']
            my_log.info("获取备份列表")
        except Exception as e:
            my_log.error(f"获取备份失败: {e}")

    def backup_recovery(self, backup_name, *recovery_item):
        """
        触发备份恢复
        :param backup_name: 备份 id
        :param recovery_item: 待恢复项 1 产品定义 2 测试实施 4 通用参数 8 AGV 配置文件
        :return:
        """
        self.get_occupy()
        try:
            # 触发恢复,61是取，72是放。这个需要提前写定用于做校验 "recoveryItems": [2],
            data = {"id": self.backup_lst[backup_name]['id'], "recoveryItems": recovery_item,"universalParameterRecoveryItems": [1]}
            response_data = self.request_post(Backup_Recovery_URL, data)
            print(response_data)
        except Exception as e:
            my_log.error(f"触发备份{backup_name}失败: {e}")
        finally:
            self.get_unoccupy()

    def backup_status(self):
        """
        查询备份恢复进度是否完成
        :return:
        """
        pass

def clear_robotune_task():
    requests.post(ClearExistTask_URL)
    print("等待robotune清除缓存")
    time.sleep(1)
    print("robotune缓存已清除")

    # todo-启动前确认地图和agv初始位置。根据webots的初始位姿态来处理？好像也不错。或者根据任务里面的移动任务的起点来处理。


if __name__ == "__main__":


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


    # 开启常用服务
    a = AGVsysTrigger()
    a.StartALLInstance()

    # 关闭所有服务
    # a = AGVsysTrigger()
    # a.GetAllServiceInstance()
    # print(a.ServiceInstanceList)
    # a.StopALLInstance()
    # exit()

    # try:
    #     taskId = 71  # 示例 taskid
    #     loopNum = 1  # 示例 loopnum
    #     task_trigger = TaskTrigger()
    #     task_trigger.get_occupy()
    #     task_trigger.post_debug_flow(taskId,loopNum)
    #     task_trigger.get_unoccupy()
    # except Exception as e:
    #     my_log.error(f"程序执行过程中发生错误: {e}")

    # 触发自主回归路径，但是需要计算的路径点，还需要点击确定和继续任务。是否需要触发使用错误码获取，是否需要继续也使用错误码获取
    # auto_back_url = 'http://127.0.0.1:24311/api/services/task/AutoBackTask/CreateTask'
    # tk = TaskTrigger()
    # body_5 = {
    #     'pathString': '',
    #     'isConfirm': True,
    # }
    # rp = tk.make_request(url=auto_back_url, data=body_5)
    # print(rp)

    # 本地刷新缓存，暂没看出作用
    # refresh_cache = 'http://127.0.0.1:24311/api/services/sys/Localization/RefreshCache'
    # tk = TaskTrigger()
    # rp = tk.make_request(url=refresh_cache, data={})
    # print(rp)



    # 自主路径返回，获取错误码是脱轨，触发请求规划（暂无），创建任务执行此时任务是执行中，再次获取到任务是暂停+没有脱轨错误码，启动
    # auto_back = f'http://127.0.0.1:24311/api/services/task/AutoBackTask/CreateTask'
    # pathString = ""
    # body_3 = {
    #     "pathString": pathString,
    #     "isConfirm": True
    # }
    # rp2 = requests.post(url=auto_back, data=body_3)

    # 循环执行多个任务流程列表
    # tk = TaskTrigger()
    # for i in [493, 494]:
    #     tk.get_occupy()
    #     loop_num = 1
    #     rep = tk.post_debug_flow(i, loopNum=1)
    #     tk.get_unoccupy()
    #     task_id = rep['result']
    #     # task_id = 1427ef6b-83dd-42da-be94-e511bb85e0c7
    #     while True:
    #         url_GetCurrentTaskInfo = f"http://127.0.0.1:24311/api/services/task/DynamicFlow/GetDebugStatus?taskId={task_id}"
    #         rep1 = requests.get(url_GetCurrentTaskInfo)
    #         finish_status = rep1.json()['result']['status']['finish']
    #         taskStatus = rep1.json()['result']['status']['taskStatus']
    #         if taskStatus == 'paused':
    #             response = requests.get(f"http://127.0.0.1:24311/api/services/pm/WarningRecord/GetAll?Level=4")
    #             # print(json.dumps(response.json(),indent=2, ensure_ascii=False))
    #             error_code = response.json()['result']['items'][0]['errorCode']
    #             if error_code == '0x02400C52':
    #                 body_2 = {"buttonType": 2,"operType": 2,"params": "True"}
    #                 reset_url = 'http://127.0.0.1:24311/api/services/task/Agv/SetCtrButton'
    #                 rp1 = tk.make_request(url=reset_url, data=body_2)
    #                 time.sleep(1)
    #                 body_2 = {"buttonType": 4, "operType": 4, "params": "True"}
    #                 reset_url = 'http://127.0.0.1:24311/api/services/task/Agv/SetCtrButton'
    #                 rp2 = tk.make_request(url=reset_url, data=body_2)
    #                 time.sleep(1)
    #                 body_2 = {"buttonType": 3, "operType": 3, "params": "True"}
    #                 reset_url = 'http://127.0.0.1:24311/api/services/task/Agv/SetCtrButton'
    #                 rp3 = tk.make_request(url=reset_url, data=body_2)
    #         print(finish_status)
    #         time.sleep(5)
    #         if finish_status:
    #             time.sleep(5)
    #             break

    # 执行任务
    # tk = TaskTrigger()
    # tk.get_occupy()
    # servo_palletconv_id = 151
    # loopNum = 1
    # rep = tk.post_debug_flow(servo_palletconv_id, loopNum=1)
    # task_id = rep['result']
    # tk.get_unoccupy()

    # 获取当前任务信息，这个接口感觉有问题，不应该能获取到，返回的结果中有当前正在执行的任务id和任务是取货loading还是等待stop
    # cti = f"http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo"
    # rp = requests.get(url=cti)
    # current_task_id = rp.json()['result']['taskId']
    # print(rp.json())
    #
    # # # 获取任务状态，尤其是单个innerTaskId在不断变动
    # # tk = TaskTrigger()
    # # # tk.get_DebugStatus()
    # # task_id = "7c623ca7-f5bb-4c0b-905c-5a8d10e28f0f"
    # debugstatus = f"{BASE_URL}/services/task/DynamicFlow/GetDebugStatus?taskId={current_task_id}"
    # rep = requests.get(debugstatus)
    # inner_task_id = rep.json()['result']['innerTaskId']  # 用于终止任务
    # inner_task_id = rep.json()['result']['groupSorting']  # 当前任务索引
    # print(rep.json()['result']['status']['taskStatus'])  # 当前任务状态用于判断是不是暂停
    # print(rep.json())
    # print(inner_task_id)

    # 终止任务
    # tk = TaskTrigger()
    # tk.get_occupy()
    # # 需要 GetDebugStatus 获取到的当前正在执行的 innerTaskID
    # shutdown_task_url = f"http://127.0.0.1:24311/api/services/task/Agv/CtrlTaskStatus"
    # body_1 = {
    #     "taskId": f"92B8A5C2-5565-4929-BF08-0A974D6754CD",
    #     "operType": 0,
    #     "operTypeExpand": 0
    # }
    # tk.make_request(url=shutdown_task_url, data=body_1)
    # tk.get_unoccupy()

    # 2是复位
    # tk = TaskTrigger()
    # tk.get_occupy()
    # body_2 = {"buttonType": 2, "operType": 2, "params": "True"}
    # reset_url = 'http://127.0.0.1:24311/api/services/task/Agv/SetCtrButton'
    # rp = tk.make_request(url=reset_url, data=body_2)
    # tk.get_unoccupy()

    # 暂停、复位、启动、手动完成.3是启动
    # tk = TaskTrigger()
    # tk.get_occupy()
    # body_2 = {"buttonType": 3,"operType": 3,"params": "True"}
    # reset_url = 'http://127.0.0.1:24311/api/services/task/Agv/SetCtrButton'
    # rp = tk.make_request(url=reset_url, data=body_2)
    # tk.get_unoccupy()



    # 获取当前所有任务流程列表id
    # url_task_list = ("http://127.0.0.1:24311/api/services/task/DynamicFlow/GetAll?MaxResultCount=100")
    # rp = requests.get(url=url_task_list)
    # print(json.dumps(rp.json()['result']['items'], indent=2, ensure_ascii=False))
    # """简化插孔 495 简化墩孔494 简化卷积493 伺服卷积151"""

    # 获取一个任务流程列表中的所有单步任务包括 id，对应的分区 id
    # task_info_url = ("http://127.0.0.1:24311/api/services/task/DynamicFlow/GetFlowInfo?Id=493")
    # rp = requests.get(task_info_url)
    # print(json.dumps(rp.json(), indent=2, ensure_ascii=False))

    # # 利用分区 id 获取分区名称、map ID、vnl名称
    # url_get_districtId = ("http://127.0.0.1:24311/api/services/task/DynamicFlow/GetDistrict?districtId=26")
    # rp = requests.get(url=url_get_districtId)
    # print(rp.json())

    # 利用分区 id 获取地图名称
    # map_District_url = ("http://127.0.0.1:24311/api/services/map/District/Get?Id=26")
    # rp = requests.get(url=map_District_url)
    # print(rp.json())

    # 获取级别2的最近错误码
    # response = requests.get(f"http://127.0.0.1:24311/api/services/pm/WarningRecord/GetAll?Level=4")
    # print(json.dumps(response.json(),indent=2, ensure_ascii=False))
    # print(response.json()['result']['items'][0]['errorCode'])

    # 获取当前任务状态，但是没成功，AgvTask 是单任务调试，VoiceFlow 是语音调试，DynamicFlow 是动态调试，TaskFlow 是静态
    # task_satus = f"http://127.0.0.1:24311/api/services/task/AgvTask/GetCurrentDebugStatus"
    # rp = requests.get(url=task_satus)
    # print(rp.status_code)
    # print(rp.headers)
    # print(rp.text)
    # print(rp.json())
