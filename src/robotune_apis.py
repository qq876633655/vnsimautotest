# -*- coding: utf-8 -*-

import os
import time
import requests
import json
from src.log import my_log

# 从环境变量中读取敏感信息
CLIENT_ID = os.getenv("CLIENT_ID", "afbecef7cd2d37e99b28a46ab1d01f4f")
XSRF_TOKEN = os.getenv("XSRF_TOKEN",
                       "CfDJ8CLpIqq3xxxLjgPMz28yvcIkcamlefVJLtByKCRcVYrCtUzZm_AqTXSiTnvmwWWaMZKLTgWSeeNFkSEpaVQyoo0ROkc"
                       "0IRcHPPYC0h8svmAL5QxqxoEBgeNbmjBlyhydWV_NcabN1GdL0i_-Zjkm7mg")
ROBOTUNE_USERNAME = os.getenv("ROBOTUNE_USERNAME", "admin")
ROBOTUNE_PASSWORD = os.getenv("ROBOTUNE_PASSWORD", "123qwe")

# 定义API URL AgvTask 是单任务调试，VoiceFlow 是语音调试，DynamicFlow 是动态调试，TaskFlow 是静态
BASE_URL = "http://127.0.0.1:24311"
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
# 动态流程分区信息、地图信息、所有分区信息
GetDistrict_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetDistrict"
District_Get_URL = f"{BASE_URL}/api/services/map/District/Get"
District_GetAll_URL = f"{BASE_URL}/api/services/map/District/GetAll"
# 获取所有任务列表、清除任务缓存、任务执行、任务状态、任务详情、正在运行中的任务
DF_GetAll_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetAll"
ClearExistTask_URL = f"{BASE_URL}/api/services/task/DynamicFlow/ClearExistTask"
DebugFlow_URL = f"{BASE_URL}/api/services/task/DynamicFlow/DebugFlow"
GetDebugStatus_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetDebugStatus"
GetFlowInfo_URL = f"{BASE_URL}/api/services/task/DynamicFlow/GetFlowInfo"
GetCurrentTaskInfo_URL = f"{BASE_URL}/api/services/task/Agv/GetCurrentTaskInfo"
# 通参一级节点获取、通参二级及以下参数获取
GetAllNodes_URL = f"{BASE_URL}/api/services/pm/CommonParameter/GetAllNodes"
GetRootNodes_URL = f"{BASE_URL}/api/services/pm/CommonParameter/GetRootNodes"
# 错误码获取、终止、复位启动
WarningRecord_GetAll_URL = f"{BASE_URL}/api/services/pm/WarningRecord/GetAll"
CtrlTaskStatus_URL = f"{BASE_URL}/api/services/task/Agv/CtrlTaskStatus"
SetCtrlButton_URL = f"{BASE_URL}/api/services/task/Agv/SetCtrButton"
# 自动回归
AutoBackTask_CreateTask_URL = f"{BASE_URL}/api/services/task/AutoBackTask/CreateTask"

# 可能有用的
"http://127.0.0.1:24311/api/services/task/AgvTask/GetCurrentDebugStatus"
'http://127.0.0.1:24311/api/services/sys/Localization/RefreshCache'

def start_robotune():
    pass

def stop_robotune():
    pass

def start_docker():
    pass

def stop_docker():
    pass


class RobotuneInstance:
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "Authorization": "null",
            'Content-Type': 'application/json-patch+json',
            "X-XSRF-TOKEN": XSRF_TOKEN,
        }
        self.get_authorization()
        self.task_loop_normal_exit = False  # 不知道干啥用
        self.task_loop_exceptional_exit = False  # 不知道干啥用
        self.service_instance_lst = []  # 服务实例
        self.backup_lst = []  # 所有备份
        self.all_task_lst = []  # 当前方案所有任务列表
        self.running_task_id = ''  # 正在运行的任务id
        self.group_sorting = ''  # 正在运行的任务索引
        self.inner_task_id = '' # 正在运作的内部任务id
        self.task_status = '' # 任务状态
        self.is_finish = False # 是否完成

    def request_post(self, url, data):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            my_log.error(f"post 请求过程中发生异常: {e}")
            return None

    def request_get(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            my_log.error(f"get 请求过程中发生异常: {e}")
            return None

    def request_delete(self, url):
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            my_log.error(f"delete 请求过程中发生异常: {e}")
            return None

    def get_authorization(self):
        """
        登录获取 token
        :return:
        """
        data = {
            "userNameOrEmailAddress": ROBOTUNE_USERNAME,
            "password": ROBOTUNE_PASSWORD,
            "agvIP": "string",
            "clientId": CLIENT_ID,
            "rememberClient": True
        }
        try:
            response = self.request_post(Authenticate_URL, data)
            access_token = response['result']['accessToken']
            self.headers["Authorization"] = f'Bearer {access_token}'
            my_log.info("登录成功")
        except BaseException as e:
            my_log.error(f"登录失败：{e}")


    def reset_authorization(self):
        """
        登录断开时使用
        :return:
        """
        pass

    def get_occupy(self):
        """
        获取控制权
        :return:
        """
        data = {
            "clientId": CLIENT_ID,
            "remark": 'auto_test_lgc'
        }
        try:
            response = self.request_post(Occupy_URL, data)
            if response['success']:
                my_log.info("获取控制权成功")
            else:
                raise
        except BaseException as e:
            my_log.error(f"获取控制权失败: {e}")

    def get_unoccupy(self):
        """
        释放控制权
        :return:
        """
        data = {}
        try:
            self.request_post(UnOccupy_URL, data)
            my_log.info("释放控制权成功")
        except Exception as e:
            my_log.error(f"释放控制权失败: {e}")

    def get_all_service_id(self):
        """
        获取所有产品定义中的服务 id
        :return:
        """
        try:
            response = self.request_get(GetAllServiceInstance_URL)
            if response['success']:
                self.service_instance_lst = response['result']['data']
                my_log.info(f"获取所有服务id成功")
            else:
                my_log.error(f"获取所有服务id失败：{response['error']}")
            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except BaseException as e:
            my_log.error(f"获取所有服务id异常: {e}")

    def start_instance(self, service_id, service):
        """
        启动一个服务
        :param service_id:
        :param service:
        :return:
        """
        try:
            data = {"Id": service_id}
            response = self.request_post(StartInstance_URL, data)
            if response['success']:
                my_log.info(f"启动{service}服务成功：{service_id}")
        except BaseException as e:
            my_log.error(f"启动{service}服务异常: {e}")

    def stop_instance(self, service_id, service):
        """
        关闭一个服务
        :param service_id:
        :param service:
        :return:
        """
        try:
            data = {"Id": service_id}
            response = self.request_post(StopInstance_URL, data)
            if response['success']:
                my_log.info(f"停止{service}服务成功：{service_id}")
        except BaseException as e:
            my_log.error(f"停止{service}服务异常: {e}")

    def start_agv_instance(self):
        """
        启动 agv 相关服务，此方法稳定性低，尤其是 general
        :return:
        """
        try:
            if not self.service_instance_lst:
                raise "未获取到服务id"
            for data in self.service_instance_lst:
                if data['serviceType']['serviceTypeName'] == 'perception':
                    self.start_instance(data['id'], 'perception')
                elif data['serviceType']['serviceTypeName'] == '3DSlamPrinter':
                    self.start_instance(data['id'], '3DSlamPrinter')
                elif data['serviceType']['serviceTypeName'] == 'general':
                    self.start_instance(data['id'], 'general')
                elif data['serviceType']['serviceTypeName'] == '3DSlam':
                    self.start_instance(data['id'], '3DSlam')
            my_log.info("启动 agv 所有服务成功")
        except BaseException as e:
            my_log.error(f"启动 agv 所有服务异常：{e}")

    def stop_all_instance(self):
        """
        关闭所有服务
        :return:
        """
        try:
            for data in self.service_instance_lst:
                self.stop_instance(data['id'], data['serviceType']['serviceTypeName'])
            my_log.info("停止 agv 所有服务成功")
        except BaseException as e:
            my_log.error(f"停止 agv 所有服务异常{e}")

    def service_status(self, service_id):
        """
        获取服务状态，ecal 查询相关 topic 启动状态
        :param service_id:
        :return:
        """
        pass

    def backup_get_all(self, max_result_count=100, page_index=1):
        """
        获取备份列表
        :param max_result_count:
        :param page_index:
        :return:
        """
        try:
            get_all_url = Backup_GetAll_URL + f"?MaxResults={max_result_count}&PageIndex={page_index}"
            response = self.request_get(get_all_url)
            self.backup_lst = response['result']['items']
            my_log.info("获取备份列表成功")
        except BaseException as e:
            my_log.error(f"获取备份异常: {e}")

    def backup_recovery(self, rb_backup_name):
        """
        触发备份恢复，待恢复项 1 产品定义 2 测试实施 4 通用参数 8 AGV 配置文件
        :param rb_backup_name: 备份名称
        :return:
        """
        try:
            # detect_put-V5.2.1.0_test-20250611143618 detect_get-V5.2.1.0_test-20250604110917
            self.get_occupy()
            backup_id = 0
            backup_items = []
            for backup in self.backup_lst:
                if backup['name'] == rb_backup_name:
                    backup_id = backup['id']
                    backup_items = [i['value'] for i in backup['backupItems']]
            data = {"id": backup_id, "recoveryItems": backup_items,"universalParameterRecoveryItems": [1]}
            response = self.request_post(Backup_Recovery_URL, data)
            if response['success']:
                my_log.info(f"触发备份{rb_backup_name}成功")
            else:
                my_log.error(f"触发备份{rb_backup_name}失败")
        except BaseException as e:
            my_log.error(f"触发备份{rb_backup_name}异常: {e}")
        finally:
            self.get_unoccupy()

    def backup_status(self):
        """
        查询备份恢复进度是否完成，在该方法成功后必须调用一次 get_all_flow_info
        :return:
        """
        pass

    def get_all_flow_info(self):
        #{'name': '货柜车放货', 'attributeFrom': 0, 'moveTaskId': 7,
        # 'moveTaskName': None, 'creationTime': '2025-05-28 15:40:16:433',
        # 'lastUpdateTime': '0001-01-01 00:00:00:000', 'doCount': 0,
        # 'schemeId': 141, 'schemeName': None, 'id': 176}
        """
        获取全部任务列表，在测试实施恢复后需要刷新一次
        :return:
        """
        try:
            response = self.request_get(DF_GetAll_URL)
            self.all_task_lst = response['result']['items']
            my_log.info("获取当前方案所有任务列表信息成功")
        except BaseException as e:
            my_log.error(f"获取当前方案所有任务列表信息异常: {e}")

    def get_flow_info(self, single_task_lst_id):
        """
        获取一个任务列表
        :param single_task_lst_id: 单个任务列表 id
        :return:
        """
        # {'name': '通用取货', 'moveTaskId': 7, 'moveTaskDistrictId': 0, 'moveTaskDisplayName': '通用移动',
        #  'taskCreateType': 1, 'taskGroups': [{'groupId': 3335, 'name': '默认任务组', 'taskTpls': [
        #     {'vertexList': ['52'], 'agvTaskId': 6, 'parkType': 1, 'configType': 0, 'districtId': 26,
        #      'agvTaskDisplayName': '通用取货', 'agvTaskTypeId': 3, 'agvTaskTypeName': 'Loading',
        #      'agvTaskTypeDisplayName': '取货', 'information': '', 'schemeId': 128,
        #      'taskType': {'unionId': None, 'name': 'Loading', 'displayName': '取货', 'requiredPark': True, 'sort': 0,
        #                   'enumValue': 4, 'remark': None, 'id': 3}, 'id': 8770},
        #     {'vertexList': ['100,140,-90'], 'agvTaskId': 7, 'parkType': 0, 'configType': 0, 'districtId': 26,
        #      'agvTaskDisplayName': '通用移动', 'agvTaskTypeId': 2, 'agvTaskTypeName': 'MoveTo',
        #      'agvTaskTypeDisplayName': '移动', 'information': '', 'schemeId': 128,
        #      'taskType': {'unionId': None, 'name': 'MoveTo', 'displayName': '移动', 'requiredPark': False, 'sort': 0,
        #                   'enumValue': 3, 'remark': None, 'id': 2}, 'id': 8771}]}], 'schemeId': 128,
        #  'schemeName': '通用取货', 'id': 163}

        # 获取一个任务流程列表中的所有单步任务包括 id，对应的分区 id
        try:
            get_flow_info_url = GetFlowInfo_URL + f"?id={single_task_lst_id}"
            response = self.request_get(get_flow_info_url)
            # print(response['result'])
            my_log.info("获取当前方案一个任务列表信息成功")
            return response['result']
        except BaseException as e:
            my_log.error(f"获取当前方案一个任务列表信息异常: {e}")

    def get_root_nodes(self):
        """
        获取一级节点 uuid
        :return:
        """
        root_nodes = self.request_get(GetRootNodes_URL)
        nodes_dict = {}
        for i in root_nodes['result']['childNodes']:
            nodes_dict[i['nodeName']] = i['uuid']
        my_log.info("获取通参一级节点")
        return nodes_dict

    def get_nodes_args(self,root_nodes_name, key):
        """
        获取一级节点下的参数，用关键字会获得多个，还需要再处理
        :param root_nodes_name:
        :param key:
        :return:
        """
        nodes_dict = self.get_root_nodes()
        get_all_nodes = GetAllNodes_URL + f"?uuid={nodes_dict[root_nodes_name]}&key={key}"
        args_value = self.request_get(get_all_nodes)
        my_log.info(f"获取通参：root_nodes_name={root_nodes_name}，key={key}")
        return args_value['result']

    def get_district_info(self, district_name):
        """
        根据分区名称获取分区 ID、地图 ID、地图名称、vnl 文件名称
        :param district_name:
        :return:
        """
        # {'name': '取放仿真测试分区', 'locationName': 'map_20250530154407', 'number': '01', 'mapId': 13,
        #   'mapName': '取放仿真测试', 'remark': '', 'vnlFileId': 538, 'vnlFileName': 'detect_put.vnl', 'yamlFileId': 536,
        #   'yamlFileName': 'map.yaml',
        #   'yamlFileContent': '{"image": "map.png", "resolution": "0.020000", "origin": ["49.500000", "39.419998", "0.000000"], "occupied_thresh": "0.65", "free_thresh": "0.196", "negate": "1"}\n',
        #   'backgroundFileId': 537, 'backgroundFileName': 'map.png', 'levelNum': 1, 'maxParkNumOnEachLevel': 100000,
        #   'lastModificationTime': '2025-06-18 13:03:22:617', 'type': 0, 'typeName': '作业', 'mapPositioningType': 0,
        #   'mapPositioningTypeName': '3Dslam', 'mapPositioningRecordId': 10,
        #   'mapPositioningRecordName': '取放仿真测试地图',
        #   'mapPositioningRecord': {'name': '取放仿真测试地图', 'locationName': 'map_20250530154407',
        #                            'backgroundFileId': 537, 'backgroundFileName': 'map.png',
        #                            'backgroundFilterFileId': 1814, 'backgroundFilterFileName': 'filter_map.png',
        #                            'yamlFileId': 536, 'yamlFileName': 'map.yaml', 'isExistFolder': False,
        #                            'yamlFileContent': '{"image": "map.png", "resolution": "0.020000", "origin": ["49.500000", "39.419998", "0.000000"], "occupied_thresh": "0.65", "free_thresh": "0.196", "negate": "1"}\n',
        #                            'limitedRelocationROIs': [], 'id': 10},
        #   'coordinateLeftTop': 'Map.DistrictBoundaryCoordinate',
        #   'coordinateLeftBottom': 'Map.DistrictBoundaryCoordinate',
        #   'coordinateRightTop': 'Map.DistrictBoundaryCoordinate',
        #   'coordinateRightBottom': 'Map.DistrictBoundaryCoordinate', 'parkMode': ['SingleDirection'],
        #   'isConfigured': True, 'syncVnl': True, 'showVnlFile': True, 'enable': True, 'id': 26}

        district_get_url = District_GetAll_URL + f"?name={district_name}"
        response = self.request_get(district_get_url)
        my_log.info(f"获取分区信息成功：district_name={district_name}")
        return response['result']['items'][0]

        # # 利用分区 id 获取分区名称、map ID、vnl名称
        # get_district_url = GetDistrict_URL + f"?DistrictId=26"
        # response_district = self.request_get(get_district_url)
        # print(response_district)
        # # 利用分区 id 获取地图名称
        # district_get_url = District_Get_URL + f"?Id=26"
        # response_map = self.request_get(district_get_url)
        # print(response_map)

    def reset_localization(self):
        """
        触发重定位
        :return:
        """
        pass

    def switch_map(self):
        """
        切换地图
        :return:
        """
        pass

    def debug_flow(self, task_name, loop_num=0, start_task_group_index=0, start_index=0):
        """
        执行一次任务，任务执行前必须通过 get_all_flow_info 获取最新的任务列表
        :param task_name:
        :param loop_num:
        :param start_task_group_index: 单步任务在任务列表中的组索引
        :param start_index: 单步任务在任务列表中的单个索引
        :return:
        """
        try:
            self.get_occupy()
            task_id = ''
            for i in self.all_task_lst:
                if i['name'] == task_name:
                    task_id = i['id']
            data = {
                "id": task_id,
                "doCount": loop_num,
                "startTaskGroupIndex": start_task_group_index,
                "startIndex": start_index
            }
            response = self.request_post(DebugFlow_URL, data)
            if response['success']:
                self.running_task_id = response['result']
                my_log.info(f"下发运行任务成功：task_name={task_name}，group_index={start_task_group_index}，index={start_index}")
            else:
                my_log.warning(response['error'])
            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        except BaseException as e:
            my_log.error(f"下发运行任务异常：task_name={task_name}，group_index={start_task_group_index}，index={start_index}，{e}")
            self.running_task_id = False
        finally:
            self.get_unoccupy()

    def get_running_task_info(self):
        """
        获取正在运行的任务信息
        :return:
        """
        # 获取当前任务信息，这个接口感觉有问题，不应该能获取到，返回的结果中有当前正在执行的任务id和任务是取货loading还是等待stop
        try:
            response = self.request_get(GetCurrentTaskInfo_URL)
            # print(response)
            if response['success']:
                self.running_task_id = response['result']['taskId']
                my_log.info(f"获取运行中任务id成功：{self.running_task_id}")
            else:
                my_log.info("获取运行中任务失败")
        except BaseException as e:
            self.running_task_id = False
            my_log.error(f"获取运行中任务id异常：{e}")

    def get_debug_status(self):
        """
        获取执行任务状态，innerTaskId 用于复位启动等，groupSorting 当前任务索引用于中止复位后执行
        finish 用于判断任务是否完成，taskStatus 用于判断是否被暂停做错误码获取 completed 完成 canceled 取消 paused 暂停

        重启前都要调用一次这个刷新执行索引
        :return:
        """
        try:
            # 单个 innerTaskId 在不断变动，需要咨询下 innerTaskId 是不是持续变化且唯一的
            self.get_running_task_info()
            response = self.request_get(GetDebugStatus_URL + f"?taskId={self.running_task_id}")
            self.inner_task_id = response['result']['innerTaskId']
            self.group_sorting = response['result']['groupSorting']
            self.task_status = response['result']['status']['taskStatus']
            self.is_finish = response['result']['status']['finish']
            # print(response)
            if response['result']['status']['finish'] == True:
                self.task_loop_normal_exit = True
            if response['result']['status']['taskStatus'] == 'paused':
                self.task_loop_exceptional_exit = True
            my_log.info(f'获取运行中任务状态成功：{self.running_task_id}')
        except BaseException as e:
            my_log.error(f"获取运行中任务状态异常: {e}")

    def get_warning(self, level=None, max_result_count=3):
        """
        默认获取最近的 3 4 等级下各 3个错误码，在错误码处理函数中应该用时间判断，需要判断单个错误码和组合错误码
        :param level:
        :param max_result_count:
        :return:
        """
        # {'level': '4', 'moduleId': 2, 'errorCode': '0x02400004', 'startTimestamp': 1750237651783, 'endTimestamp': 0,
        #  'serviceType': {'serviceTypeId': '0x02', 'serviceTypeName': 'Tasks', 'serviceTypeName_zh': '任务',
        #                  'serviceTypeDestription': '', 'createTime': '0001-01-01 00:00:00:000', 'serviceCompany': 0,
        #                  'id': 5274},
        #  'warning': {'errorCode': '0x02400004', 'sysName': None, 'name': '下位机长时间通讯同步异常',
        #              'warningDestription': None, 'moduleCode': None, 'levelCode': None,
        #              'createTime': '0001-01-01 00:00:00:000', 'id': 0}, 'id': 'b351b858-c01d-4a14-8721-9cae0e2a94cd'}
        try:
            if level is None:
                level = [3, 4]
            error_code = []
            for i in level:
                error_code_url = WarningRecord_GetAll_URL + f"?Level={i}&maxResults={max_result_count}"
                response = self.request_get(error_code_url)
                error_code.extend(response['result']['items'])
            # print(error_code)
            my_log.info(f"获取错误码成功：leval={level}，max_result_count={max_result_count}")
            return error_code
        except BaseException as e:
            my_log.error(f"获取错误码异常：leval={level}，max_result_count={max_result_count}，{e}")
            return None

    def ctrl_task_status(self, oper_type=0, oper_type_expand=0):
        """
        控制任务
        :param oper_type: 0-取消 1-暂停 2-恢复 3-更新 4-外部完成
        :param oper_type_expand: oper_type = 0 时，0-中止 1-跳过
        :return:
        """
        try:
            self.get_occupy()
            self.get_debug_status()
            data = {
                "taskId": self.inner_task_id,
                "operType": oper_type,
                "operTypeExpand": oper_type_expand
            }
            response = self.request_post(CtrlTaskStatus_URL, data)
            if response['success']:
                my_log.info(f"控制任务成功：oper_type={oper_type}，oper_type_expand={oper_type_expand}")
        except BaseException as e:
            my_log.error(f"控制任务异常：oper_type={oper_type}，oper_type_expand={oper_type_expand}，{e}")
        finally:
            self.get_unoccupy()

    def set_ctr_button(self, button_type):
        """
        设置车辆状态
        :param button_type: 0-急停 1-暂停 2-复位 3-启动 4-手动完成
        :return:
        """
        try:
            data = {"buttonType": button_type, "operType": button_type, "params": True}
            response = self.request_post(SetCtrlButton_URL, data)
            if response['success']:
                my_log.info(f"设置车辆状态成功：button_type={button_type}")
            else:
                my_log.info(f"设置车辆状态失败：button_type={button_type}")
            # print(response)
        except BaseException as e:
            my_log.error(f"设置车辆状态异常：button_type={button_type}，{e}")

    def reset_start(self, suspend=False, done=False):
        """
        复位和终止启动
        :param suspend: 终止时用
        :param done: 需要完成任务时用
        :return:
        """
        try:
            if suspend:
                self.ctrl_task_status(0, 0)
                time.sleep(1)
            self.set_ctr_button(2)
            time.sleep(1)
            if done:
                self.set_ctr_button(4)
                time.sleep(1)
            self.set_ctr_button(3)
            time.sleep(1)
            my_log.info(f"重置启动成功，suspend={suspend}，done={done}")
        except BaseException as e:
            my_log.error(f"重启启动异常，suspend={suspend}，done={done}，{e}")

    def get_auto_back(self):
        """
        获取自动回归路径规划
        :return:
        """
        pass

    def auto_back_create(self):
        data = {
            "pathString": "string",
            "isConfirm": True
        }
        # 自主路径返回，获取错误码是脱轨，触发请求规划（暂无），创建任务执行此时任务是执行中，再次获取到任务是暂停+没有脱轨错误码，启动
        # 触发自主回归路径，但是需要计算的路径点，还需要点击确定和继续任务。是否需要触发使用错误码获取，是否需要继续也使用错误码获取
        response = self.request_post(AutoBackTask_CreateTask_URL, data)
        print(response.json())

    def clear_exist_task(self):
        try:
            data = {}
            self.request_post(ClearExistTask_URL, data)
            time.sleep(1)
            my_log.info("robotune缓存已清除")
        except BaseException as e:
            my_log.error(f"robotune缓存清除异常：{e}")


if __name__ == "__main__":
    test_item = [
        {
            "wbt_name":"",
            "district_name":"",
            "backup_name":"",
            "task_name_lst":[],
        }
    ]
    rb_api = RobotuneInstance()
    # rb_api.reset_authorization()
    # rb_api.get_occupy()
    # rb_api.get_unoccupy()
    # rb_api.get_all_service_id()
    # rb_api.start_agv_instance()
    # rb_api.stop_all_instance()
    # rb_api.backup_get_all()
    # print(rb_api.backup_lst)
    # rb_api.backup_recovery("detect_get-V5.2.1.0_test-20250604110917")
    # rb_api.get_all_flow_info()
    # print(rb_api.all_task_lst)
    # rb_api.get_flow_info(163)
    # rb_api.get_root_nodes()
    # rb_api.get_nodes_args("静态参数", '货叉长度')
    # rb_api.get_district_info('取放')
    # rb_api.get_all_flow_info()
    # rb_api.debug_flow('伺服固定放货法')
    # rb_api.get_running_task_info()
    # rb_api.get_debug_status()
    # rb_api.get_warning()
    # print(rb_api.inner_task_id)
    # rb_api.ctrl_task_status(0, 0)
    # rb_api.set_ctr_button(2)
    # rb_api.reset_start(suspend=True)
    # rb_api.clear_exist_task()

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
