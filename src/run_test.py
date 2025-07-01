# -*- coding: utf-8 -*-
"""
Time:2025/6/19 18:08
Author:yanglei
File:dd_robot.py
"""

import json
import subprocess

from src.docker_wbt import DockerWbt, stop_all_docker
from src.robotune_obj import RobotuneOBJ, start_robotune, stop_robotune
from src.vn_ecal import *
from common.operate_doc import CSVCaseManager, create_file_copy
from common.utils import *
from common.decorators import thread
from config.auto_test_cfg import *
import time
import os

sim_auto_test_db = [
    {
        'test_version': '5.2.1.12_250321_test',
        'test_vehicle': 'P15_fwd_3mid360_bw_2mid360',
        'scheme_name': '感知取货',
        'config_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/P15_fwd_3mid360_bw_2mid360/config',
        'multilidar_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/P15_fwd_3mid360_bw_2mid360/MultiLidar.yaml',
        'product_name': 'p15-V5.2.1.0_test-20250624095606',
        'wbt_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/P15_fwd_3mid360_bw_2mid360/get/detect_get_p.wbt',
        'lastagvpose_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/P15_fwd_3mid360_bw_2mid360/get/lastagvpose',
        'implementation_name': 'demo_detect_get-V5.2.1.0_test-20250624190825',
    },
    {
        'test_version': '5.2.1.12_250321_test',
        'test_vehicle': 'P15_fwd_3mid360_bw_2mid360',
        'scheme_name': '感知放货',
        'config_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/P15_fwd_3mid360_bw_2mid360/config',
        'multilidar_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/P15_fwd_3mid360_bw_2mid360/MultiLidar.yaml',
        'product_name': 'p15-V5.2.1.0_test-20250624095606',
        'wbt_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/P15_fwd_3mid360_bw_2mid360/put/detect_put_p.wbt',
        'lastagvpose_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/P15_fwd_3mid360_bw_2mid360/put/lastagvpose',
        'implementation_name': 'demo_detect_put-V5.2.1.0_test-20250624192209',
    },
    {
        'test_version': '5.2.1.12_250321_test',
        'test_vehicle': 'E35_fwd_3mid360_bw_2mid360',
        'scheme_name': '感知取货',
        'config_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/config',
        'multilidar_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/MultiLidar.yaml',
        'product_name': 'E35-V5.2.1.0_test-20250623201855',
        'wbt_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/get/detect_get_e.wbt',
        'lastagvpose_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/get/lastagvpose',
        'implementation_name': 'demo_detect_get-V5.2.1.0_test-20250624190825',
    },
    {
        'test_version': '5.2.1.12_250321_test',
        'test_vehicle': 'E35_fwd_3mid360_bw_2mid360',
        'scheme_name': '感知放货',
        'config_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/config',
        'multilidar_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/MultiLidar.yaml',
        'product_name': 'E35-V5.2.1.0_test-20250623201855',
        'wbt_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/put/detect_put_p.wbt',
        'lastagvpose_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/put/lastagvpose',
        'implementation_name': 'demo_detect_put-V5.2.1.0_test-20250624192209',
    },
]

dw_obj, rb_obj, current_product_name, current_implementation_name = None, None, None, None


def get_test_items(test_config, test_version):
    """
    从测试配置中获取测试项
    :param test_version:
    :param test_config:
    :return:
    """
    # test_items = [
    #     {
    #         'test_vehicle': 'P15_fwd_3mid360_bw_2mid360',
    #         'status': '',
    #         'product_name': '',
    #         'config_path': '',
    #         'multilidar_path': '',
    #         'test_scheme_lst': [
    #             {'wbt_path': '', 'lastagvpose_path': '', 'implementation_name': '', 'status': '',
    #              'scheme_name': '感知取货',
    #              'test_task_lst': [
    #                  {'task_name': '伺服卷积托盘冒烟', 'loop_num': 1, 'status': ''},
    #              ]
    #              },
    #         ],
    #     },
    # ]
    test_items = test_config.copy()
    for v_t in test_config:
        test_vehicle = v_t['test_vehicle']
        for _ in sim_auto_test_db:
            if _['test_vehicle'] == test_vehicle and _['test_version'] == test_version:
                v_t['status'] = ''
                v_t['product_name'] = _['product_name']
                v_t['config_path'] = _['config_path']
                v_t['multilidar_path'] = _['multilidar_path']
                break
        for v_t_i in v_t['test_scheme_lst']:
            for _ in sim_auto_test_db:
                if _['test_vehicle'] == test_vehicle and _['test_version'] == test_version and _[
                    'scheme_name'] == v_t_i['scheme_name']:
                    v_t_i['status'] = ''
                    v_t_i['wbt_path'] = _['wbt_path']
                    v_t_i['implementation_name'] = _['implementation_name']
                    v_t_i['lastagvpose_path'] = _['lastagvpose_path']
                    break
            for test_task in v_t_i['test_task_lst']:
                test_task['status'] = ''
                test_task['loop_num'] = 1
    return test_items


def get_test_cases(test_config, cases_path):
    """
    从测试配置中筛选测试用例
    :param test_config:
    :param cases_path:
    :return:
    """
    cp_case_path = create_file_copy(cases_path)
    filter_lst = []
    for i in test_config:
        for j in i['test_scheme_lst']:
            for k in j['test_task_lst']:
                filter_lst.append({'任务流程列表': k['task_name'], '测试车型': i['test_vehicle']})
    cases_temp = CSVCaseManager(cases_path)
    cases_temp.read()
    tc_mg = cases_temp.filter_and_save_as(cp_case_path, filter_lst)
    return tc_mg


def check_backup(test_items, backup_lst):
    """

    :return:
    """
    test_items_backup = []
    for item in test_items:
        test_items_backup.append(item['product_name'])
        for scheme in item['test_scheme_lst']:
            test_items_backup.append(scheme['implementation_name'])
    backup_lst = [i['name'] for i in backup_lst]
    missing = list(set(test_items_backup) - set(backup_lst))
    if missing:
        raise my_log.warning(f'待测试备份不在备份恢复中：{missing}')
    else:
        my_log.info(f"待测备份检查成功")
        return True


def replace_vehicle(rb_obj, product_name, config_paht, multilidar_path):
    """
    替换车型的 general/config、perception/config/MultiLidar、备份的产品定义+通参
    :param rb_obj:
    :return:
    """
    global current_product_name
    if product_name == current_product_name:
        return False
    else:
        subprocess.run(f"rm -rf {GENERAL_PATH}/config", shell=True, check=True)
        subprocess.run(f"cp -r {config_paht} {GENERAL_PATH}", shell=True, check=True)
        my_log.info(f'替换config目录：{config_paht}')
        subprocess.run(f"cp -r {multilidar_path} {PERCEPTION_PATH}/config", shell=True, check=True)
        my_log.info(f'替换多雷达文件：{multilidar_path}')
        rb_obj.backup_recovery(product_name)
        time.sleep(30)
        current_product_name = product_name
        return True


def replace_lastagvpose_implementation(rb_obj, lastagvpose_path, implementation_name):
    """
    替换 lastagvpose、实施方案
    :param rb_obj:
    :return:
    """
    global current_implementation_name
    if implementation_name == current_implementation_name:
        return False
    else:
        subprocess.run(f"rm -rf {SLAM_PATH}/lastagvpose", shell=True, check=True)
        subprocess.run(f"cp -r {lastagvpose_path} {SLAM_PATH}", shell=True, check=True)
        my_log.info(f'替换lastagvpose目录：{lastagvpose_path}')
        rb_obj.backup_recovery(implementation_name)
        time.sleep(60)
        current_implementation_name = implementation_name
        return True


def only_one_robotune_page():
    """
    只保留一个 robotune 窗口
    :return:
    """
    pass


def comparison_pose(sim_vehicle_pose: Pose, sim_fork_pose: Pose, test_case):
    """
    位姿比较，无仿真货叉 z 暂不比较，其他精度要求也可以做参数，目前写死
    :param sim_vehicle_pose:
    :param sim_fork_pose:
    :param test_case:
    :return:
    """
    case_status = '已通过'
    if abs(float(test_case['预期x']) - sim_vehicle_pose.x) > 0.01:
        case_status = '未通过'
    if abs(float(test_case['预期y']) - sim_vehicle_pose.y) > 0.01:
        case_status = '未通过'
    if abs(float(test_case['预期z']) - sim_fork_pose.z) > 100:
        case_status = '未通过'
    if abs(float(test_case['预期yaw']) - sim_vehicle_pose.yaw) > 1:
        case_status = '未通过'
    test_case['仿真x'] = sim_vehicle_pose.x
    test_case['仿真y'] = sim_vehicle_pose.y
    test_case['仿真z'] = sim_fork_pose.z
    test_case['仿真yaw'] = sim_vehicle_pose.yaw
    test_case['用例状态'] = case_status
    if case_status == '已通过':
        my_log.debug(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}位姿比较已通过')
    else:
        my_log.warning(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}位姿比较未通过')


def check_all_test(test_items):
    all_test = True
    for item in test_items:
        if item['status'] is None:
            all_test = False
            return all_test
        for scheme in item['test_scheme_lst']:
            if scheme['status'] is None:
                all_test = False
                return all_test
            for test_task in scheme['test_task_list']:
                if test_task['status'] is None:
                    all_test = False
                    return all_test
    return all_test


@thread('start')
def run_test(test_items, tc_mg, docker_file_path):
    """
    主运行函数
    :return:
    """
    # 关闭 robotune 和所有容器，再启动 robotune 后关闭自启动服务，实例化一个 robotune 对象，然后获取全部备份列表
    global dw_obj, rb_obj
    stop_all_docker()
    stop_robotune()
    time.sleep(3)
    start_robotune()
    time.sleep(20)
    rb_obj = RobotuneOBJ()
    rb_obj.get_all_service_id()
    rb_obj.stop_all_instance()
    rb_obj.backup_get_all()
    check_backup(test_items, rb_obj.backup_lst)

    # 循环测试项，从车型开始
    restart_num = 1
    while True:
        if check_all_test(test_items):
            break
        try:
            for item in test_items:
                if item['status'] == 'done':
                    continue
                test_vehicle = item['test_vehicle']
                replace_vehicle(rb_obj, product_name=item['product_name'], config_paht=item['config_path'],
                                multilidar_path=item['multilidar_path'])
                rb_obj.get_all_service_id()

                # 循环测试 wbt、实施方案、lastagvpose
                for test_scheme in item['test_scheme_lst']:
                    if test_scheme['status'] == 'done':
                        continue

                    # 换 lastagvpose、实施方案
                    replace_lastagvpose_implementation(rb_obj, lastagvpose_path=test_scheme['lastagvpose_path'],
                                                       implementation_name=test_scheme['implementation_name'])

                    # 重写并启动一个容器拉起所有 wbt，然后拉起 agv 服务
                    stop_all_docker()
                    dw_obj = DockerWbt(test_scheme['wbt_path'], flag_start_with_bright_eye=False)
                    dw_obj.load(dw_obj.wbt_file)
                    dw_obj.get_controller_wbt_lst()
                    dw_obj.prepare_wbt_file()
                    dw_obj.start_docker(docker_file_path)
                    if not is_ecal_wbt_alive(30):
                        raise Exception('wbt 启动失败')
                    rb_obj.start_agv_instance()
                    if not is_ecal_services_alive(30):
                        raise Exception('服务 启动失败')

                    # Todo 此处需要一个重定位成功的方法，目前用等待吧，理论上可以重定位成功

                    # 循环待测任务列表
                    rb_obj.get_all_flow_info()
                    for test_task in test_scheme['test_task_lst']:
                        if test_task['status'] == 'done':
                            continue

                        rb_obj.reset_start()
                        rb_obj.debug_flow(task_name=test_task['task_name'], loop_num=test_task['loop_num'],
                                          start_task_group_index=0, start_index=0)

                        # 轮询当前任务状态
                        while True:
                            rb_obj.get_running_task_info()
                            rb_obj.get_debug_status()
                            test_case = tc_mg.get_row_by_conditions(
                                {'标题': rb_obj.running_group_name, '测试车型': test_vehicle,
                                 '任务流程列表': test_task['task_name']}
                            )
                            error_code_lst = rb_obj.get_warning()
                            if rb_obj.running_task_type == 'Stop':
                                pose = get_pose_once()
                                sim_vehicle_pose = axis_angle_to_rpy(
                                    translation_=[pose.position.x, pose.position.y, pose.position.z],
                                    rotation_=[pose.orientation.x, pose.orientation.y, pose.orientation.z,
                                               pose.orientation.w])
                                sim_fork_pose = Pose(z=0)
                                comparison_pose(sim_vehicle_pose, sim_fork_pose, test_case)
                                tc_mg.save()

                            # Todo 出问题时并不是所有都是 Stop or paused 状态，有些还在执行中，但是车停止动了，这种需要
                            if rb_obj.running_task_status == 'paused':
                                # 错误码解决部分不太好写，先判断获取到的和预期的有交集就复位完成继续
                                # Todo 用暂停不行，测伺服空间放货的时候一直3级错误码但不暂停

                                error_code = [error['errorCode'] for error in error_code_lst]
                                expect_error_code_lst = parse_string_to_list(test_case['预期错误码'])
                                set_value = set(error_code) & set(expect_error_code_lst)
                                if set_value:
                                    my_log.debug(
                                        f"{test_task['task_name']}+{rb_obj.running_group_name}触发预期错误码{set_value}")
                                    rb_obj.reset_start(done=True)
                                    test_case['用例状态'] == '已通过'
                                    tc_mg.save()
                                else:
                                    is_occasionally = rb_obj.handle_error_code(error_code_lst)
                                    # Todo 此处写一个非预期错误码处理方法，包括不限于重启 docker、重启服务、重启 robotune
                                    # Todo 差一个异常错误码时的日志记录，目前在想要不就直接重启 docker、重启服务，这样也方便获取日志
                                    # Todo 或者只记录个时间点算了，这样在所有服务跑完之后用一个函数到时间点拿数据，但是日志容易覆盖包括离线数据
                                    my_log.warning(
                                        f"{test_task['task_name']}+{rb_obj.running_group_name}触发非预期错误码{error_code_lst}")
                                    rb_obj.reset_start(done=True)
                                    test_case['用例状态'] == '未通过'
                                    tc_mg.save()
                            if rb_obj.running_is_finish:
                                test_task['status'] = 'done'
                                break
                            time.sleep(3)
                    dw_obj.stop_docker()
                    dw_obj.delete_copy_wbt()
                    rb_obj.stop_all_instance()
                    test_scheme['status'] = 'done'
                    time.sleep(10)
                item['status'] = 'done'
        except Exception as e:
            my_log.warning(f"意外重启第{restart_num}次")
            restart_num += 1
        finally:
            dw_obj.stop_docker()
            dw_obj.delete_copy_wbt()
            rb_obj.stop_all_instance()
            time.sleep(10)
    stop_robotune()



def main(test_config, test_version, get_put_csv_path, docker_file_path):
    """
    初始化
        全局参数-严重问题和数量
        读取静态配置、动态配置、用例配置
            从用例配置筛选用例并创建用例文档
        返回一个整个测试运行配置项
    启动线程本地资源监控
        启动一个shell脚本做日志记录
    启动线程测试执行，在主进程结束时结束
    启动线程ecal数据监控
    日志分析
        结束资源分析线程，对资源日志图表分析
        定位结果记录到本地，测了哪些用例。找吴頔问建图和扩展建图评分
        对算法模块做日志分析
            感知
            定位
            控制
    测试结果钉钉提示
    :return:
    """
    test_items = get_test_items(test_config, test_version)
    print(json.dumps(test_items, indent=4, ensure_ascii=False))
    tc_mg = get_test_cases(test_config, get_put_csv_path)
    start_ecal_listener()
    run_test(test_items, tc_mg, docker_file_path)
    print("============================================================================")


if __name__ == '__main__':
    get_put_csv_path = r"../test_case/get_put_sim_case_temp.csv"
    docker_file_path = r"../startDockerSimTest.sh"
    test_version = '5.2.1.12_250321_test'
    test_config = [
        {
            'test_vehicle': 'P15_fwd_3mid360_bw_2mid360',
            'test_scheme_lst': [
                {
                    'scheme_name': '感知取货',
                    'test_task_lst': [
                        {'task_name': '伺服卷积托盘冒烟'},
                        # {'task_name': '伺服墩孔检测冒烟'},
                    ]
                },
                {
                    'scheme_name': '感知放货',
                    'test_task_lst': [
                        {'task_name': '伺服固定放货法冒烟'},
                        # {'task_name': '伺服空间放货法冒烟'},
                    ]
                }
            ],
        },
        {
            'test_vehicle': 'E35_fwd_3mid360_bw_2mid360',
            'test_scheme_lst': [
                {
                    'scheme_name': '感知取货',
                    'test_task_lst': [
                        # {'task_name': '伺服卷积托盘冒烟'},
                        {'task_name': '伺服墩孔检测冒烟'},
                    ]
                },
                {
                    'scheme_name': '感知放货',
                    'test_task_lst': [
                        # {'task_name': '伺服固定放货法冒烟'},
                        {'task_name': '伺服空间放货法冒烟'},
                    ]
                }
            ],
        },
    ]
    # main(test_config, test_version, get_put_csv_path, docker_file_path)
    get_test_items(test_config, test_version)
    # rb_obj = RobotuneOBJ()
    # rb_obj.backup_get_all()
    # check_backup(test_items, rb_obj.backup_lst)
    # start_listener()
    # time.sleep(2)
    # sim_vehicle_pose = get_sim_vehicle_pose()
    # test_case = {'标题': '识别到载具', '测试车型': 'P15_fwd_3mid360_bw_2mid360', '任务流程列表': '伺服卷积托盘冒烟',
    #              '预期x': '100', '预期y': '140', '预期z': '0.1', '预期yaw': '90', '预期错误码': '',
    #              '仿真x': '', '仿真y': '', '仿真z': '', '仿真yaw': '', '用例状态': ''}
    # sim_fork_pose = Pose(z=0.1)
    # comparison_pose(sim_vehicle_pose,sim_fork_pose, test_case)
    # print(test_case)
