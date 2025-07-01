# -*- coding: utf-8 -*-
"""
Time:2025/6/19 18:08
Author:yanglei
File:dd_robot.py
"""

import os
import time
import requests
import json
import subprocess
from common.log import my_log

# 从环境变量中读取敏感信息
CLIENT_ID = os.getenv("CLIENT_ID", "afbecef7cd2d37e99b28a46ab1d01f4f")
XSRF_TOKEN = os.getenv("XSRF_TOKEN",
                       "CfDJ8CLpIqq3xxxLjgPMz28yvcIkcamlefVJLtByKCRcVYrCtUzZm_AqTXSiTnvmwWWaMZKLTgWSeeNFkSEpaVQyoo0ROkc"
                       "0IRcHPPYC0h8svmAL5QxqxoEBgeNbmjBlyhydWV_NcabN1GdL0i_-Zjkm7mg")
ROBOTUNE_USERNAME = os.getenv("ROBOTUNE_USERNAME", "admin")
ROBOTUNE_PASSWORD = os.getenv("ROBOTUNE_PASSWORD", "123qwe")
SUDO_PWD = '123'

# 定义API URL AgvTask 是单任务调试，VoiceFlow 是语音调试，DynamicFlow 是动态调试，TaskFlow 是静态
BASE_URL = "http://127.0.0.1:24311"
# 登录、获取控制权、释放控制权
Authenticate_URL = f"{BASE_URL}/api/TokenAuth/Authenticate"
Occupy_URL = f"{BASE_URL}/api/services/sys/TempPermission/Occupy"
UnOccupy_URL = f"{BASE_URL}/api/services/sys/TempPermission/UnOccupy"
# 备份获取、恢复、导入、删除
Backup_GetAll_URL = f"{BASE_URL}/api/services/sys/Backup/GetAll"
Backup_Recovery_URL = f"{BASE_URL}/api/services/sys/Backup/Recovery"
Backup_Import_URL = f"{BASE_URL}/api/services/sys/Backup/Import"
Backup_Delete_URL = f"{BASE_URL}/api/services/sys/Backup/Delete"
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
Get_ForkLength_URL = f"{BASE_URL}/api/services/task/CommonParameter/GetFOrkLength"
# 错误码获取、终止、复位启动
WarningRecord_GetAll_URL = f"{BASE_URL}/api/services/pm/WarningRecord/GetAll"
CtrlTaskStatus_URL = f"{BASE_URL}/api/services/task/Agv/CtrlTaskStatus"
SetCtrlButton_URL = f"{BASE_URL}/api/services/task/Agv/SetCtrButton"
# 自动回归
AutoBackTask_CreateTask_URL = f"{BASE_URL}/api/services/task/AutoBackTask/CreateTask"
GetVehiclePosition_URL = f"{BASE_URL}/api/services/task/Agv/GetVehiclePosition"

# 可能有用的
"http://127.0.0.1:24311/api/services/task/AgvTask/GetCurrentDebugStatus"
'http://127.0.0.1:24311/api/services/sys/Localization/RefreshCache'


def start_robotune():
    """
    启动 robotune
    :return:
    """
    # command = (
    #     "sudo -S env LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/home/visionnav/AGVServices/lib dotnet /home/visionnav/AGVServices/robotune/robotune/VN.Robotune.dll"
    # )
    # result = subprocess.Popen(command, cwd="/home/visionnav/AGVServices/robotune/robotune",shell=True,
    #                           stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    cmd = "sudo -S /home/visionnav/AGVServices/AGVPro/startupRobotune.sh"
    result = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, text=True)
    result.stdin.write(f"{SUDO_PWD}\n")
    result.stdin.flush()
    num = 30
    while num:
        result = subprocess.run("ps aux | grep robotune | grep -v grep", shell=True, text=True, capture_output=True)
        lines = result.stdout.strip().splitlines()
        if len(lines) >= 5:
            my_log.info(f'启动 robotune 成功')
            return True
        else:
            my_log.debug(f'启动 robotune 计时：{num}')
            num -= 1
            time.sleep(1)
    raise my_log.error(f'启动 robotune 失败')


def stop_robotune():
    """
    停止 robotune
    :return:
    """
    try:
        shutdown_path = "/home/visionnav/AGVServices/AGVPro/shutdown.sh"
        result = subprocess.run(["sudo", "-S", shutdown_path], input=SUDO_PWD + "\n", stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        my_log.info(f'关闭 robotune 成功')
    except BaseException as e:
        raise my_log.error(f'关闭 robotune 异常：{e}')


class RobotuneOBJ:
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
        self.service_id_lst = []  # 服务实例
        self.backup_lst = []  # 所有备份
        self.all_task_lst = []  # 当前方案所有任务列表
        self.running_task_id = ''  # 运行任务id
        self.running_group_sorting = ''  # 运行任务索引
        self.running_inner_task_id = '' # 运行内部任务id
        self.running_task_status = '' # 运行任务状态
        self.running_is_finish = False # 运行任务是否完成
        self.running_flow_name = '' # 运行任务流程名称
        self.running_group_name = '' # 运行任务组名称
        self.running_task_type = '' # 运行任务类型

    def _post(self, url, data, msg):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise my_log.error(f"{msg} post 网络请求失败: {e}")
        except ValueError:
            raise my_log.error(f"{msg} post 响应不是合法 JSON")

    def _get(self, url, msg):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise my_log.error(f"{msg} get 网络请求失败: {e}")
        except ValueError:
            raise my_log.error(f"{msg} get 响应不是合法 JSON")

    def _delete(self, url, msg):
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise my_log.error(f"{msg} delete 网络请求失败: {e}")
        except ValueError:
            raise my_log.error(f"{msg} delete 响应不是合法 JSON")

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
        response = self._post(Authenticate_URL, data, '登录')
        access_token = response['result']['accessToken']
        self.headers["Authorization"] = f'Bearer {access_token}'
        my_log.info("登录成功")

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
        data = {"clientId": CLIENT_ID, "remark": 'auto_test_lyang'}
        response = self._post(Occupy_URL, data, '获取控制权')
        if response['success']:
            my_log.info("获取控制权成功")

    def get_unoccupy(self):
        """
        释放控制权
        :return:
        """
        data = {}
        response = self._post(UnOccupy_URL, data, '释放控制权')
        if response['success']:
            my_log.info("释放控制权成功")

    def get_all_service_id(self):
        """
        获取所有产品定义中的服务 id
        :return:
        """
        response = self._get(GetAllServiceInstance_URL, '获取所有服务id')
        if response['success']:
            self.service_id_lst = response['result']['data']
            my_log.info(f"获取所有服务id成功")
        else:
            raise my_log.error(f"获取所有服务id失败：{response['error']}")
        self.task_loop_normal_exit = False
        self.task_loop_exceptional_exit = False

    def start_instance(self, service_id, service):
        """
        启动一个服务
        :param service_id:
        :param service:
        :return:
        """
        data = {"Id": service_id}
        response = self._post(StartInstance_URL, data, f'启动{service}服务')
        if response['success']:
            time.sleep(1)
            my_log.info(f"启动{service}服务成功：{service_id}")
        else:
            raise my_log.error(f"开启{service}服务失败")

    def stop_instance(self, service_id, service):
        """
        关闭一个服务
        :param service_id:
        :param service:
        :return:
        """
        data = {"Id": service_id}
        response = self._post(StopInstance_URL, data, f'停止{service}服务')
        if response['success']:
            my_log.info(f"停止{service}服务成功：{service_id}")
        else:
            raise my_log.error(f"关闭{service}服务失败")

    def start_agv_instance(self):
        """
        启动 agv 相关服务，此方法稳定性低，尤其是 general
        :return:
        """
        if not self.service_id_lst:
            raise my_log.error("未获取到服务id")
        for data in self.service_id_lst:
            if data['serviceType']['serviceTypeName'] == 'general':
                self.start_instance(data['id'], 'general')
        for data in self.service_id_lst:
            if data['serviceType']['serviceTypeName'] == 'perception':
                self.start_instance(data['id'], 'perception')
        for data in self.service_id_lst:
            if data['serviceType']['serviceTypeName'] == '3DSlamPrinter':
                self.start_instance(data['id'], '3DSlamPrinter')
        for data in self.service_id_lst:
            if data['serviceType']['serviceTypeName'] == '3DSlam':
                self.start_instance(data['id'], '3DSlam')
        my_log.info("启动 agv 所有服务成功")

    def stop_all_instance(self):
        """
        关闭所有服务
        :return:
        """
        for data in self.service_id_lst:
            self.stop_instance(data['id'], data['serviceType']['serviceTypeName'])
        my_log.info("停止 agv 所有服务成功")

    def service_status(self, service_id):
        """
        获取服务状态，ecal 查询相关 topic 启动状态
        :param service_id:
        :return:
        """
        pass

    def backup_get_all(self, max_result_count=100):
        """
        获取备份列表
        :param max_result_count:
        :param page_index:
        :return:
        """
        # [{'name': 'demo_detect_put-V5.2.1.0_test-20250625191248', 'agvModel': 'demo_detect_put',
        #   'version': 'V5.2.1.0_test', 'size': 4791393, 'normalSize': '4.569MB', 'backupItem': 2,
        #   'backupItems': [{'name': '测试实施', 'value': 2}], 'processLabel': 8, 'processLabelName': '作业',
        #   'categoryLabel': 1, 'categoryLabelName': '生产', 'description': '系统备份',
        #   'creationTime': '2025-06-25 19:12:48:928', 'id': 318}]
        get_all_url = Backup_GetAll_URL + f"?MaxResulCount={max_result_count}"
        response = self._get(get_all_url, f"获取备份列表")
        self.backup_lst = response['result']['items']
        if self.backup_lst:
            my_log.info("获取备份列表成功")
        else:
            raise my_log.error("备份列表为空")

    def backup_recovery(self, rb_backup_name):
        """
        触发备份恢复，待恢复项 1 产品定义 2 测试实施 4 通用参数 8 AGV 配置文件
        universalParameterRecoveryItems 1 2 4 表示 静态参数 标定参数 其他
        :param rb_backup_name: 备份名称
        :return:
        """
        self.get_occupy()
        try:
            backup_id = 0
            backup_items = []
            for backup in self.backup_lst:
                if backup['name'] == rb_backup_name:
                    backup_id = backup['id']
                    backup_items = [i['value'] for i in backup['backupItems']]
            data = {"id": backup_id, "recoveryItems": backup_items,"universalParameterRecoveryItems": [1, 2, 4]}
            response = self._post(Backup_Recovery_URL, data, '触发备份恢复')
            if response['success']:
                my_log.info(f"触发备份恢复{rb_backup_name}成功，id：{backup_id} 备份恢复项：{backup_items}")
            else:
                raise my_log.error(f"触发备份恢复{rb_backup_name}失败")
        finally:
            self.get_unoccupy()

    def backup_status(self):
        """
        查询备份恢复进度是否完成，在该方法成功后必须调用一次 get_all_flow_info
        :return:
        """
        pass

    def backup_delete(self, backup_id):
        """
        备份删除
        :return:
        """
        backup_delete_url = Backup_Delete_URL + f"?Id={backup_id}"
        response = self._delete(backup_delete_url, '触发备份删除')
        my_log.info(f"触发备份删除成功，id：{backup_id}")

    def backup_delete_type(self, delete_type):
        """
        删除不同类型备份
        :param delete_type:
        :return:
        """
        if not self.backup_lst:
            raise my_log.warning("备份列表为空，执行一次 backup_get_all")
        for backup in self.backup_lst:
            if delete_type == '系统备份':
                if backup['description'] == delete_type:
                    self.backup_delete(backup['id'])
            if delete_type == '所有备份':
                self.backup_delete(backup['id'])
        my_log.info(f"删除不同类型备份{delete_type}")

    # 没通过测试
    def backup_import(self, file_path):
        """
        备份导入
        :return:
        """
        filename = os.path.basename(file_path)
        data = {}
        with open(file_path, 'rb') as f:
            files = {'backupFile': (
                filename,
                f,
                "application/octet-stream"
            )}
            response = requests.post(url=Backup_Import_URL,headers=self.headers,data=data, files=files)
        print(response.json())
        print(response.status_code)
        print(response.text)
        my_log.info(f"备份导入成功：{file_path}")

    # 没通过测试
    def backup_import_sim_res(self):
        """
        导入仿真资源中的所有备份
        :return:
        """
        sim_res_bak = "/home/visionnav/VNSim/sim_res_bak/test_case/get_put/"
        output = subprocess.check_output(f'find {sim_res_bak} -type f -name "*_test-??????????????.zip"',
                                         universal_newlines=True, shell=True)
        file_lst = []
        seen = set()
        for line in output.splitlines():
            if line.strip():
                filename = os.path.basename(line)
                if filename not in seen:
                    seen.add(filename)
                    file_lst.append(line)
                    print(line)
        print("****************************************************************************************")
        print(f"筛选{sim_res_bak}路径匹配*_test-??????????????.zip的备份且去重文件名一模一样的，如果不对请自行修改代码或将待导入备份改名")
        print("****************************************************************************************")
        confirm_import = input("认真查看所有zip路径，确认导入输入y或Y，否则输入其他")
        if confirm_import == 'y' or confirm_import == 'Y':
            for p in file_lst:
                self.backup_import(p)
                my_log.info(f"导入匹配成功的备份成功")
        else:
            my_log.info(f"未导入备份")

    def get_all_flow_info(self):
        #{'name': '货柜车放货', 'attributeFrom': 0, 'moveTaskId': 7,
        # 'moveTaskName': None, 'creationTime': '2025-05-28 15:40:16:433',
        # 'lastUpdateTime': '0001-01-01 00:00:00:000', 'doCount': 0,
        # 'schemeId': 141, 'schemeName': None, 'id': 176}
        """
        获取全部任务列表，在测试实施恢复后需要刷新一次
        :return:
        """
        response = self._get(DF_GetAll_URL, '获取全部任务列表')
        self.all_task_lst = response['result']['items']
        if self.all_task_lst:
            my_log.info("获取当前方案所有任务列表信息成功")
        else:
            raise my_log.warning("任务列表为空")

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
        get_flow_info_url = GetFlowInfo_URL + f"?id={single_task_lst_id}"
        response = self._get(get_flow_info_url, '获取一个任务列表')
        # print(response['result'])
        my_log.info("获取当前方案一个任务列表信息成功")
        return response['result']

    def get_root_nodes(self):
        """
        获取一级节点 uuid
        :return:
        """
        root_nodes = self._get(GetRootNodes_URL, '获取一级节点')
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
        # [{'uuid': '8c0a5fac-1803-42a4-939f-dfa59aaa1234', 'parentUUID': '81c70f73-e2d9-49b7-b81d-2ca447377750',
        #   'nodeType': 1, 'level': 2, 'nodeCode': 3, 'nodeName': '属具相关配置', 'systemName': 'Accessory',
        #   'dataTypeId': None, 'parameterUnit': None, 'valueRange': None, 'checkType': 0, 'verifyExpression': None,
        #   'parameterValue': None, 'parameterDefaultValue': None, 'parameterDestriottion': '', 'isEdit': True,
        #   'isShow': True, 'path': 'config/static/Accessory', 'tagId': None, 'tag': None, 'tagName': None,
        #   'modifyTime': '2025-03-17 16:28:17:934', 'isSearchExportNode': True, 'rangeExplain': None,
        #   'lstEnumExplain': [], 'childNodes': [
        #         {'uuid': '562ad8ed-5d90-4d74-81b7-1850628e7a23', 'parentUUID': '8c0a5fac-1803-42a4-939f-dfa59aaa1234',
        #          'nodeType': 0, 'level': 3, 'nodeCode': 45, 'nodeName': '货叉推出后的前悬距',
        #          'systemName': 'LoadPositionX', 'dataTypeId': '11', 'parameterUnit': '米(m)', 'valueRange': '非NaN',
        #          'checkType': 1, 'verifyExpression': '^(?!NaN)[+-]?\\d+(\\.\\d+)?$', 'parameterValue': '-0.13',
        #          'parameterDefaultValue': '-0.133', 'parameterDestriottion': '针对R & MR车为货叉推出后的前悬距',
        #          'isEdit': True, 'isShow': True, 'path': 'config/static/Accessory/LoadPositionX', 'tagId': None,
        #          'tag': None, 'tagName': None, 'modifyTime': '2025-03-18 13:50:26:458', 'isSearchExportNode': False,
        #          'rangeExplain': None, 'lstEnumExplain': [], 'childNodes': [], 'id': 65796}], 'id': 62900}]
        nodes_dict = self.get_root_nodes()
        get_all_nodes = GetAllNodes_URL + f"?uuid={nodes_dict[root_nodes_name]}&key={key}"
        args_value = self._get(get_all_nodes, '获取节点通参')
        my_log.info(f"获取通参：root_nodes_name={root_nodes_name}，key={key}")
        return args_value['result']

    def get_loadpositionx(self):
        result = self.get_nodes_args('静态参数', 'LoadPositionX')
        return float(result[0]['childNodes'][0]['parameterValue'])

    def get_forklength(self):
        response = self._get(Get_ForkLength_URL, '获取货叉长度')
        if response['success']:
            return response['result']
        return None

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
        response = self._get(district_get_url, '获取分区信息')
        my_log.info(f"获取分区信息成功：district_name={district_name}")
        return response['result']['items'][0]

        # # 利用分区 id 获取分区名称、map ID、vnl名称
        # get_district_url = GetDistrict_URL + f"?DistrictId=26"
        # response_district = self._get(get_district_url)
        # print(response_district)
        # # 利用分区 id 获取地图名称
        # district_get_url = District_Get_URL + f"?Id=26"
        # response_map = self._get(district_get_url)
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
        :param task_name: 任务流程列表名称
        :param loop_num: 循环次数
        :param start_task_group_index: 单步任务在任务列表中的组索引
        :param start_index: 单步任务在任务列表中的单个索引
        :return:
        """
        self.get_occupy()
        try:
            task_id = ''
            if not self.all_task_lst:
                raise BaseException("未获取最新的任务列表，执行 get_all_flow_info 试试")
            for i in self.all_task_lst:
                if i['name'] == task_name:
                    task_id = i['id']
            data = {
                "id": task_id,
                "doCount": loop_num,
                "startTaskGroupIndex": start_task_group_index,
                "startIndex": start_index
            }
            response = self._post(DebugFlow_URL, data, '执行任务')
            if response['success']:
                self.running_task_id = response['result']
                my_log.info(f"下发运行任务成功：task_name={task_name}，group_index={start_task_group_index}，index={start_index}")
            else:
                my_log.warning(response['error'])
            self.task_loop_normal_exit = False
            self.task_loop_exceptional_exit = False
        finally:
            self.get_unoccupy()

    def get_running_task_info(self):
        """
        获取正在运行的任务信息，正在执行的任务id和任务类型 Stop MoveTo Loading
        这个接口感觉有问题，不应该能获取到
        :return:
        """
        # 获取当前任务信息，，返回的结果中有当前是取货loading还是等待stop
        response = self._get(GetCurrentTaskInfo_URL, '获取运行中任务')
        # print(response)
        if response['success']:
            self.running_task_id = response['result']['taskId']
            self.running_task_type = response['result']['taskTypeName']
            # my_log.info(f"获取运行中任务id成功：{self.running_task_id}")
        else:
            my_log.info("获取运行中任务失败")

    def get_debug_status(self):
        """
        获取执行任务状态，innerTaskId 用于复位启动等，groupSorting 当前任务索引用于中止复位后执行
        finish 用于判断任务是否完成，taskStatus 用于判断是否被暂停做错误码获取 completed 完成 canceled 取消 paused 暂停

        重启前都要调用一次这个刷新执行索引
        :return:
        """
        # {'result': {'taskId': 'a0a21eba-0f57-4542-b012-1f9c27d60044', 'repeatCount': 1, 'repeatIndex': 1,
        #             'taskCount': 2, 'taskIndex': 0, 'keyTaskIndex': 0, 'flowName': '伺服卷积托盘', 'flowId': 151,
        #             'schemeId': 104, 'logicTaskId': 7526, 'isKeyTask': False, 'groupSorting': 0, 'information': None,
        #             'innerTaskId': '14AE8DDE-2D44-4365-AD96-D9E598E026A1',
        #             'status': {'taskStatus': 'paused', 'taskPercent': 10, 'finish': False},
        #             'agvTask': {'id': 7, 'name': 'CommonMove', 'displayName': '通用移动',
        #                         'taskType': {'id': 2, 'name': 'MoveTo', 'displayName': '移动', 'requiredPark': False},
        #                         'districtId': 26}, 'taskGroup': {'groupId': 3657, 'groupName': '识别到载具'},
        #             'parkNumber': None, 'fullPathIds': [107224, 107585, 107578, 107616, 107617],
        #             'endCoordinates': '95.6,153.275', 'startCoordinates': '100,125.659', 'sourceSys': 'robotune'},
        #  'targetUrl': None, 'success': True, 'error': None, 'unAuthorizedRequest': False, '__abp': True}
        # {'result': {'taskId': '302b98d1-dde5-49ef-a5b0-7829af3688b7', 'repeatCount': 1, 'repeatIndex': 1,
        #             'taskCount': 1, 'taskIndex': 0, 'keyTaskIndex': 1, 'flowName': '伺服卷积托盘', 'flowId': 151,
        #             'schemeId': 104, 'logicTaskId': 7506, 'isKeyTask': True, 'groupSorting': 0, 'information': '',
        #             'innerTaskId': '968DDB04-79C7-4219-9DB1-38C2F1BED9EE',
        #             'status': {'taskStatus': 'transacting', 'taskPercent': 10, 'finish': False},
        #             'agvTask': {'id': 8, 'name': 'CommonWaitting', 'displayName': '通用等待',
        #                         'taskType': {'id': 1, 'name': 'Stop', 'displayName': '原地等待', 'requiredPark': False},
        #                         'districtId': 26}, 'taskGroup': {'groupId': 3657, 'groupName': '识别到载具'},
        #             'parkNumber': '', 'fullPathIds': [], 'endCoordinates': '', 'startCoordinates': '',
        #             'sourceSys': 'robotune'}, 'targetUrl': None, 'success': True, 'error': None,
        #  'unAuthorizedRequest': False, '__abp': True}
        # {'result': {'taskId': '302b98d1-dde5-49ef-a5b0-7829af3688b7', 'repeatCount': 1, 'repeatIndex': 1,
        #             'taskCount': 1, 'taskIndex': 0, 'keyTaskIndex': 1, 'flowName': '伺服卷积托盘', 'flowId': 151,
        #             'schemeId': 104, 'logicTaskId': 7504, 'isKeyTask': True, 'groupSorting': 1, 'information': '',
        #             'innerTaskId': '81AEF90C-BCDC-44BC-9A3E-FDCFC7944053',
        #             'status': {'taskStatus': 'transacting', 'taskPercent': 10, 'finish': False},
        #             'agvTask': {'id': 8, 'name': 'CommonWaitting', 'displayName': '通用等待',
        #                         'taskType': {'id': 1, 'name': 'Stop', 'displayName': '原地等待', 'requiredPark': False},
        #                         'districtId': 26},
        #             'taskGroup': {'groupId': 3658, 'groupName': '左转识别到+X+Y+YAW载具'}, 'parkNumber': '',
        #             'fullPathIds': [], 'endCoordinates': '', 'startCoordinates': '', 'sourceSys': 'robotune'},
        #  'targetUrl': None, 'success': True, 'error': None, 'unAuthorizedRequest': False, '__abp': True}

        # 单个 innerTaskId 在不断变动，需要咨询下 innerTaskId 是不是持续变化且唯一的
        response = self._get(GetDebugStatus_URL + f"?taskId={self.running_task_id}", '获取执行中任务状态')
        self.running_inner_task_id = response['result']['innerTaskId']
        self.running_group_sorting = response['result']['groupSorting']
        self.running_task_status = response['result']['status']['taskStatus']
        self.running_is_finish = response['result']['status']['finish']
        self.running_flow_name = response['result']['flowName']
        self.running_group_name = response['result']['taskGroup']['groupName']
        # print(response)
        if response['result']['status']['finish']:
            self.task_loop_normal_exit = True
        if response['result']['status']['taskStatus'] == 'paused':
            self.task_loop_exceptional_exit = True
        my_log.info(f'获取运行中任务状态成功：{self.running_task_id}')

    def get_warning(self, level:[]=None, max_result_count=1):
        """
        默认获取最近的 3 4 等级下各 1 个错误码，且时间小于 3s 内
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
        if level is None:
            level = [3, 4]
        error_code_lst = []
        for i in level:
            error_code_url = WarningRecord_GetAll_URL + f"?Level={i}&MaxResultCount={max_result_count}"
            response = self._get(error_code_url, '获取错误码')
            if time.time() - float(response['result']['items']['startTimestamp']) / 1000 < 3:
                error_code_lst.extend(response['result']['items'])
        # print(error_code)
        my_log.info(f"获取错误码成功：leval={level}，max_result_count={max_result_count}")
        return error_code_lst

    def ctrl_task_status(self, oper_type=0, oper_type_expand=0):
        """
        控制任务
        :param oper_type: 0-取消 1-暂停 2-恢复 3-更新 4-外部完成
        :param oper_type_expand: oper_type = 0 时，0-中止 1-跳过
        :return:
        """
        self.get_occupy()
        try:
            self.get_debug_status()
            data = {
                "taskId": self.running_inner_task_id,
                "operType": oper_type,
                "operTypeExpand": oper_type_expand
            }
            response = self._post(CtrlTaskStatus_URL, data, '控制任务')
            if response['success']:
                my_log.info(f"控制任务成功：oper_type={oper_type}，oper_type_expand={oper_type_expand}")
        finally:
            self.get_unoccupy()

    def set_ctr_button(self, button_type):
        """
        设置车辆状态
        :param button_type: 0-急停 1-暂停 2-复位 3-启动 4-手动完成
        :return:
        """
        data = {"buttonType": button_type, "operType": button_type, "params": True}
        response = self._post(SetCtrlButton_URL, data, '设置车辆状态')
        if response['success']:
            my_log.info(f"设置车辆状态成功：button_type={button_type}")
        else:
            my_log.info(f"设置车辆状态失败：button_type={button_type}")

    def reset_start(self, suspend=False, done=False):
        """
        复位和终止启动
        :param suspend: 终止时用
        :param done: 需要完成任务时用
        :return:
        """
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
        response = self._post(AutoBackTask_CreateTask_URL, data, '触发自动回归路径')
        print(response.json())

    def clear_exist_task(self):
        data = {}
        self._post(ClearExistTask_URL, data, 'robotune缓存')
        time.sleep(1)
        my_log.info("robotune缓存已清除")

    def get_agv_pose(self):
        """
        获取车体位姿
        :return:
        """
        # {'x': 90.01, 'y': 153.9842, 'theta': -1.5085, 'speed': 0.0, 'confidency': 0.0,
        #  'creationTime': '2025-06-25 15:26:07:199'}
        response = self._get(GetVehiclePosition_URL, '获取车体位姿')
        if response['success']:
            my_log.info("获取车体当前位姿成功")
            return response['result']
        else:
            raise Exception("获取车体当前位姿失败")


    def handle_error_code(self, error_code):
        pass



if __name__ == "__main__":
    # start_robotune()
    # stop_robotune()

    rb_obj = RobotuneOBJ()
    # rb_obj.backup_import_sim_res()
    rb_obj.backup_get_all()
    # print(rb_obj.backup_lst)
    # rb_obj.backup_delete_type('系统备份')
    # robotune_get_agv_runtime_status = f"{BASE_URL}/api/services/task/VoiceFlow/GetAGVRuntimeStatus"
    # print(rb_obj._get(robotune_get_agv_runtime_status, '1'))
    # print(rb_obj.get_forklength())

    # rb_obj.reset_authorization()
    # rb_obj.get_occupy()
    # rb_obj.get_unoccupy()
    # rb_obj.get_all_service_id()
    # rb_obj.start_agv_instance()
    # rb_obj.stop_all_instance()
    # rb_obj.backup_get_all()
    # print(rb_obj.backup_lst)
    # rb_obj.backup_recovery("p15-V5.2.1.0_test-20250624095606")
    # rb_obj.backup_recovery("E35-V5.2.1.0_test-20250623201855")
    # rb_obj.backup_recovery("demo_detect_get-V5.2.1.0_test-20250622174429")
    # rb_obj.backup_recovery("demo_detect_put-V5.2.1.0_test-20250622172943")
    # rb_obj.get_all_flow_info()
    # print(rb_obj.all_task_lst)
    # print(rb_obj.get_flow_info(151))
    # rb_obj.get_root_nodes()
    # rb_obj.get_nodes_args("静态参数", '货叉长度')
    # rb_obj.get_district_info('取放')
    # rb_obj.get_all_flow_info()
    # rb_obj.debug_flow('伺服固定放货法')
    # rb_obj.get_running_task_info()
    # rb_obj.get_debug_status()
    # rb_obj.get_warning()
    # print([error['errorCode'] for error in rb_obj.get_warning()])
    # print(rb_obj.inner_task_id)
    # rb_obj.ctrl_task_status(0, 0)
    # rb_obj.set_ctr_button(2)
    # rb_obj.reset_start(suspend=True)
    # rb_obj.clear_exist_task()