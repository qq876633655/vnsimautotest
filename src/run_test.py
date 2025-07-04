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
from src.vn_mqtt import *
from common.operate_doc import CSVCaseManager, create_file_copy
from common.utils import *
from common.decorators import thread
from config.auto_test_cfg import *
import time
import os
from get_warning import ErrorCodeSubscriber

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
        'district_name': '取放仿真测试分区',
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
        'district_name': '取放仿真测试分区',
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
        'district_name': '取放仿真测试分区',
    },
    {
        'test_version': '5.2.1.12_250321_test',
        'test_vehicle': 'E35_fwd_3mid360_bw_2mid360',
        'scheme_name': '感知放货',
        'config_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/config',
        'multilidar_path': '/home/visionnav/VNSim/sim_res_bak/version_vehicle/5.2.1.12_250321_test/vehicle_model_bak/E35_fwd_3mid360_bw_2mid360/MultiLidar.yaml',
        'product_name': 'E35-V5.2.1.0_test-20250623201855',
        'wbt_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/put/detect_put_e.wbt',
        'lastagvpose_path': '/home/visionnav/VNSim/sim_res_bak/test_case/get_put/E35_fwd_3mid360_bw_2mid360/put/lastagvpose',
        'implementation_name': 'demo_detect_put-V5.2.1.0_test-20250624192209',
        'district_name': '取放仿真测试分区',
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
                    v_t_i['district_name'] = _['district_name']
                    break
            for test_task in v_t_i['test_task_lst']:
                test_task['status'] = ''
                test_task['loop_num'] = 1
    my_log.info(f"测试配置：{json.dumps(test_items, indent=4, ensure_ascii=False)}")
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
    my_log.info(f"创建用例副本：{cp_case_path}")
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


def replace_vehicle(rb_obj, product_name, config_path, multilidar_path):
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
        subprocess.run(f"cp -r {config_path} {GENERAL_PATH}", shell=True, check=True)
        my_log.info(f'替换config目录：{config_path}')
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


def save_case_result(tc_mg, test_case, set_error=None, advanced_error_lst=None):
    pose = get_pose_once()
    sim_vehicle_pose = axis_angle_to_rpy(
        translation_=[pose.position.x, pose.position.y, pose.position.z],
        rotation_=[pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
    )
    # print(sim_vehicle_pose.__dict__)
    sim_fork_pose = Pose(z=0)
    case_status = '已通过'
    msg = ''
    contrast_x = abs(float(test_case['预期x']) - sim_vehicle_pose.x)
    contrast_y = abs(float(test_case['预期y']) - sim_vehicle_pose.y)
    contrast_z = abs(float(test_case['预期z']) - sim_fork_pose.z)
    contrast_yaw = abs(float(test_case['预期yaw']) - sim_vehicle_pose.yaw)
    if contrast_x > 0.02:
        case_status = '未通过'
        msg += f'x精度误差：{contrast_x}'
    if contrast_y > 0.02:
        case_status = '未通过'
        msg += f'y精度误差：{contrast_y}'
    if contrast_z > 100:
        case_status = '未通过'
        msg += f'z精度误差：{contrast_z}'
    if contrast_yaw > 2:
        case_status = '未通过'
        msg += f'yaw精度误差：{contrast_yaw}'
    test_case['仿真x'] = sim_vehicle_pose.x
    test_case['仿真y'] = sim_vehicle_pose.y
    test_case['仿真z'] = sim_fork_pose.z
    test_case['仿真yaw'] = sim_vehicle_pose.yaw
    # if not test_case['用例状态']:
    test_case['用例状态'] = case_status
    if set_error:
        test_case['用例状态'] = '已通过'
        test_case['实际错误码'] = set_error
        my_log.info(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}触发预期错误码{set_error}')
    elif advanced_error_lst:
        test_case['用例状态'] = '未通过'
        test_case['实际错误码'] = advanced_error_lst
        my_log.warning(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}触发非预期错误码{advanced_error_lst}')
    else:
        if case_status == '已通过':
            my_log.info(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}位姿比较已通过')
        else:
            my_log.warning(f'{test_case["测试车型"]}+{test_case["任务流程列表"]}+{test_case["标题"]}位姿比较未通过：{msg}')
    print(test_case)
    tc_mg.save()


def check_all_test(test_items):
    all_test = True
    for vehicle in test_items:
        if not vehicle['status']:
            all_test = False
            return all_test
        for scheme in vehicle['test_scheme_lst']:
            if not scheme['status']:
                all_test = False
                return all_test
            for test_task in scheme['test_task_lst']:
                if not test_task['status']:
                    all_test = False
                    return all_test
    return all_test


def reset_loc(loc_name, reset_loc_num):
    while reset_loc_num:
        if not get_localization_status():
            time.sleep(1)
            reset_loc_num -= 1
            pose = get_pose_once()
            sim_vehicle_pose = axis_angle_to_rpy(
                translation_=[pose.position.x, pose.position.y, pose.position.z],
                rotation_=[pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
            )
            if not switch_map(loc_name):
                continue
            time.sleep(1)
            if not reset_localization(loc_name, sim_vehicle_pose.x, sim_vehicle_pose.y, sim_vehicle_pose.yaw):
                continue
            time.sleep(1)
        else:
            return True
    return False

# 可能不使用新线程更好，作为主线程崩了就崩了吧。任务执行的重启放到while try中
# @thread('start')
def run_test(test_items, tc_mg, docker_file_path, error_listener):
    """
    主运行函数
    :return:
    """
    global dw_obj, rb_obj

    # 关闭 robotune 和所有容器，再启动 robotune 后关闭自启动服务，实例化一个 robotune 对象，然后获取全部备份列表
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
    restart_num = 0
    # while True:
    #     if check_all_test(test_items):
    #         break
    # try:
    for item in test_items:
        if item['status'] == 'done':
            continue
        test_vehicle = item['test_vehicle']
        replace_vehicle(rb_obj, product_name=item['product_name'], config_path=item['config_path'],
                        multilidar_path=item['multilidar_path'])
        rb_obj.get_all_service_id()

        # 循环测试 wbt、实施方案、lastagvpose
        for test_scheme in item['test_scheme_lst']:
            if test_scheme['status'] == 'done':
                continue

            replace_lastagvpose_implementation(rb_obj, lastagvpose_path=test_scheme['lastagvpose_path'],
                                               implementation_name=test_scheme['implementation_name'])

            # 重写并启动一个容器拉起所有 wbt，然后拉起 agv 服务
            rb_obj.stop_all_instance()
            dw_obj = DockerWbt(test_scheme['wbt_path'], flag_start_with_bright_eye=False)
            dw_obj.stop_docker()
            dw_obj.load(dw_obj.wbt_file)
            dw_obj.get_controller_wbt_lst()
            dw_obj.prepare_wbt_file()
            dw_obj.start_docker(docker_file_path)
            if not is_ecal_wbt_alive(30):
                raise Exception('wbt启动失败')
            rb_obj.start_agv_instance()
            if not is_ecal_services_alive(30):
                raise Exception('服务启动失败')
            if not reset_loc(test_scheme['district_name'], 3):
                raise Exception('重定位3次失败')

            # 循环待测任务列表
            rb_obj.get_all_flow_info()
            for test_task in test_scheme['test_task_lst']:
                if test_task['status'] == 'done':
                    continue
                rb_obj.clear_exist_task()
                rb_obj.reset_start()
                rb_obj.debug_flow(task_name=test_task['task_name'], loop_num=test_task['loop_num'],
                                  start_task_group_index=0, start_index=0)
                """
                1.正常可以识别且识别成功的用例，触发等待3s。
                2.正常可以识别但识别失败的用例，触发非预期高级错误码（暂停）。触发等待3s。
                3.正常不可以识别且识别失败的用例，触发预期高级错误码（暂停）。触发等待3s。
                4.正常不可以识别但识别成功的用例，触发等待3s。
                5.取放任务过程中触发非预期高级错误码（暂停）。触发等待3s。
                6.取放任务过程中触发预期高级错误码（暂停）。触发等待3s。
                7.取放任务过程中触发非预期非高级错误码（不暂停）。
                8.取放任务过程中触发预期非高级错误码（不暂停）。
                9.取放完成，等待任务过程中触发非预期高级错误码（暂停）。
                10.取放完成，等待任务过程中触发预期高级错误码（暂停）。
                11.取放完成，等待任务过程中触发非预期非高级错误码（不暂停）。
                12.取放完成，等待任务过程中触发预期非高级错误码（不暂停）
                13.过程中无错误码且车不动（不暂停）。异常逻辑，
                """
                # 轮询当前任务状态
                while True:
                    rb_obj.get_running_task_info()
                    rb_obj.get_debug_status()
                    # print(rb_obj.running_is_finish)
                    if rb_obj.running_is_finish:
                        test_task['status'] = 'done'
                        break
                    test_case = tc_mg.get_row_by_conditions(
                        {'标题': rb_obj.running_group_name, '测试车型': test_vehicle,
                         '任务流程列表': test_task['task_name']}
                        )
                    advanced_error_lst = [i for i in error_listener.get_latest_error() if
                                          i['level'] == 3 or i['level'] == 4]
                    # print(test_case)
                    if test_case['用例状态'] and not advanced_error_lst:
                        time.sleep(3)
                        continue


                    # Todo 出问题时并不是所有都是 Stop or paused 状态，有些还在执行中，但是车停止动了
                    # Todo 此处写一个非预期错误码处理方法，包括不限于重启 docker、重启服务、重启 robotune
                    # Todo 差一个异常错误码时的日志记录，目前在想要不就直接重启 docker、重启服务，这样也方便获取日志
                    # Todo 或者只记录个时间点算了，这样在所有服务跑完之后用一个函数到时间点拿数据，但是日志容易覆盖包括离线数据
                    # Todo 加一个自动处理问题模式和手动处理问题模式
                    # Todo 因为上一条用例导致的脱轨，影响了下一条测试用例的结果
                    # Todo 偶尔会有闪一帧的错误码导致用例失败，实际上可以继续运行的
                    # Todo 等待和有错误码实际上可能会同时存在，目前的方式是先执行一次等待处理，再执行错误码处理。感觉不太好
                    if rb_obj.running_task_type == 'Stop':
                        save_case_result(tc_mg, test_case)
                    # if rb_obj.running_task_status == 'paused':
                    if advanced_error_lst:
                        error_code = [error['errorcode'] for error in advanced_error_lst]
                        expect_error_code_lst = parse_string_to_list(test_case['预期错误码'])
                        set_error = set(error_code) & set(expect_error_code_lst)
                        if set_error:
                            save_case_result(tc_mg, test_case, set_error=set_error)
                            rb_obj.reset_start(done=True)
                        else:
                            save_case_result(tc_mg, test_case, advanced_error_lst=advanced_error_lst)
                            # is_occasionally = rb_obj.handle_error_code(advanced_error_lst)
                            rb_obj.reset_start(done=True)
                    time.sleep(3)
            dw_obj.stop_docker()
            dw_obj.delete_copy_wbt()
            rb_obj.stop_all_instance()
            test_scheme['status'] = 'done'
            time.sleep(10)
        item['status'] = 'done'
    # except Exception as e:
    #     restart_num += 1
    #     my_log.warning(f"意外重启第{restart_num}次：{e}")
    #     # if restart_num == 10:
    #         # break
    # finally:
    #     dw_obj.stop_docker()
    #     dw_obj.delete_copy_wbt()
    #     rb_obj.stop_all_instance()
    #     time.sleep(10)
    stop_robotune()


def main(test_config, test_version, get_put_csv_path, docker_file_path, auto_error_handling):
    """
    启动线程本地资源监控
        启动一个shell脚本做日志记录
    主进程
        循环的错误码处理部分
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
    tc_mg = get_test_cases(test_config, get_put_csv_path)
    start_ecal_listener()
    error_listener = ErrorCodeSubscriber()
    print("=====================================测试启动=======================================")
    run_test(test_items, tc_mg, docker_file_path, error_listener, auto_error_handling)
    print("=====================================测试结束=======================================")


if __name__ == '__main__':
    get_put_csv_path = r"../test_case/get_put_sim_case_temp.csv"
    docker_file_path = r"../startDockerAutoTest.sh"
    test_version = '5.2.1.12_250321_test'
    auto_error_handling = False
    test_config = [
        {
            'test_vehicle': 'P15_fwd_3mid360_bw_2mid360',
            'test_scheme_lst': [
                {
                    'scheme_name': '感知取货',
                    'test_task_lst': [
                        {'task_name': '伺服卷积托盘冒烟'},
                        {'task_name': '伺服墩孔检测冒烟'},
                    ]
                },
                {
                    'scheme_name': '感知放货',
                    'test_task_lst': [
                        {'task_name': '伺服固定放货法冒烟'},
                        {'task_name': '伺服空间放货法冒烟'},
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
                        {'task_name': '伺服卷积托盘冒烟'},
                        {'task_name': '伺服墩孔检测冒烟'},
                    ]
                },
                {
                    'scheme_name': '感知放货',
                    'test_task_lst': [
                        {'task_name': '伺服固定放货法冒烟'},
                        {'task_name': '伺服空间放货法冒烟'},
                    ]
                }
            ],
        },
    ]
    main(test_config, test_version, get_put_csv_path, docker_file_path, auto_error_handling)
    # start_ecal_listener()
    # reset_loc('map_20250612163448', 3)

    # get_test_items(test_config, test_version)
    # tc_mg = get_test_cases(test_config, get_put_csv_path)
    # test_case = tc_mg.get_row_by_conditions(
    #     {'标题': '识别到载具', '测试车型': 'P15_fwd_3mid360_bw_2mid360',
    #      '任务流程列表': '伺服卷积托盘冒烟'}
    # )
    # print(test_case)
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
