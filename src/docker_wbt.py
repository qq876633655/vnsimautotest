# -*- coding: utf-8 -*-
"""
Time:2025/6/19 18:08
Author:yanglei
File:dd_robot.py
"""

import subprocess
import os
import re
import shutil
import time

from src.webots_parser import WebotsParser
from common.log import my_log


class DockerWbt(WebotsParser):
    def __init__(self, wbt_file, flag_start_with_bright_eye=False):
        super().__init__()
        self.wbt_file = wbt_file
        self.flag_start_with_bright_eye = flag_start_with_bright_eye
        self.controller_wbt_lst = []

    def get_controller_wbt_lst(self):
        for node in self.content["root"]:
            if node["name"] == "Robot":
                if node["DEF"] == "RobotNode":
                    for field in node["fields"]:
                        if field["name"] == "customData":
                            custom_data_str = field["value"]
                            match = re.search(r"controller_list\[(.*?)]", custom_data_str)
                            if match:
                                content = match.group(1)
                                for c_type in content.split(","):
                                    self.controller_wbt_lst.append({"controller_type": c_type})
                                if self.flag_start_with_bright_eye:
                                    if "shadow_be" not in content.split(","):
                                        self.controller_wbt_lst.insert(len(self.controller_wbt_lst) - 2,
                                                                       {"controller_type": "shadow_be"})
                                my_log.info(f"匹配到控制器列表: {content}")
                            else:
                                raise my_log.error("没有匹配到控制器列表")

    def prepare_wbt_file(self):
        """
        处理 wbt 配置文件 centralWidgetVisible: 1 显示中央主窗口 0 关闭中央主窗口
        :return:
        """
        for wbt in self.controller_wbt_lst:
            # to-do :prepare .wbproj
            destination_wbt = self.wbt_file.replace(".wbt", "_" + wbt["controller_type"] + "_autotest_copy.wbt")
            shutil.copy(self.wbt_file, destination_wbt)
            my_log.info(f"File copied successfully to {destination_wbt}")

            wbt['wbt_file'] = destination_wbt
            dir_name, file_name = os.path.split(destination_wbt)
            newfile_name = file_name.replace(".wbt", ".wbproj")
            wbproj_file = os.path.join(dir_name, "." + newfile_name)
            wbt['wbproj_file'] = wbproj_file
            if "gui" in wbt["controller_type"]:
                with open(wbproj_file, "w") as file:
                    file.write("Webots Project File version R2024a\ncentralWidgetVisible: 1\n")
            else:
                with open(wbproj_file, "w") as file:
                    file.write("Webots Project File version R2024a\ncentralWidgetVisible: 0\n")

    def start_docker(self, docker_path):
        try:
            cpu_num = 0
            wbt_commands = []
            for wbt in self.controller_wbt_lst:
                if "shadow_be" in wbt['controller_type']:
                    self.handle_wbt_file_for_bright_eye(wbt['wbt_file'], wbt['controller_type'])
                else:
                    self.handle_wbt_file(wbt['wbt_file'], wbt['controller_type'])

                command = ''
                if "gui" in wbt['controller_type']:
                    command = f"webots --mode=realtime {wbt['wbt_file']}"
                else:
                    command = f"webots --mode=realtime --no-rendering --minimize {wbt['wbt_file']}"
                    if "master" in wbt['controller_type']:
                        command = f"taskset -c {cpu_num},{cpu_num + 1} " + command
                        cpu_num += 2
                    else:
                        command = f"taskset -c {cpu_num} " + command
                        cpu_num += 1
                # process = subprocess.Popen(command)
                wbt_commands.append(command)
                # self.process.append(process)
            # self.modify_docker_file(docker_path, wbt_commands)
            process = subprocess.Popen(["bash", docker_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise BaseException("启动容器异常")
            time.sleep(2)
            my_log.info("启动容器成功")
            for i, cmd in enumerate(wbt_commands):
                docker_cmd = ["docker", "exec", "-d", "vnsim_dev", "bash", "-c", cmd]
                subprocess.run(docker_cmd)
                my_log.info(f"wbt启动成功：{cmd}")
                time.sleep(1)  # 控制启动间隔
        except BaseException as e:
            raise my_log.error(f"{e}")

    @staticmethod
    def modify_docker_file(docker_path, wbt_commands):
        with open(docker_path, "r") as f:
            lines = f.readlines()
        shell_lines = []
        for cmd in wbt_commands:
            shell_lines.append(f"{cmd} & sleep 1 &&")
        shell_lines.append("tail -f /dev/null")
        new_cmd = ' '.join(shell_lines)
        new_run_cmd = f'simulation:latest bash -c "{new_cmd}"\n'
        for i, line in enumerate(lines):
            if 'simulation:latest' in line:
                lines[i] = new_run_cmd
                break
        with open(docker_path, "w") as f:
            f.writelines(lines)

    @staticmethod
    def handle_wbt_file(start_wbt_file, controller_type):
        wp = WebotsParser()
        wp.load(start_wbt_file)
        for node in wp.content["root"]:
            if node["name"] == "ConvoyerBelt":
                for field in node["fields"]:
                    if field["name"] == "controller" and "master" in controller_type:
                        field["value"] = "ConvoyerRobot"
                        my_log.info("修改ConvoyerBelt的controller为ConvoyerRobot %s", controller_type)
            if node["name"] == "Robot" and node["DEF"] == "RobotNode":
                for field in node["fields"]:
                    if field["name"] == "controller":
                        field["value"] = controller_type
                        my_log.info(f"修改{start_wbt_file}控制器：{field['value']}", )
        wp.save(start_wbt_file)

    @staticmethod
    def handle_wbt_file_for_bright_eye(start_wbt_file, controller_type):
        my_log.info("启动明眸")
        wp = WebotsParser()
        wp.load(start_wbt_file)

        for node in wp.content["root"]:
            if node["name"] == "Robot" and node["DEF"] == "RobotNode":
                for field in node["fields"]:
                    if field["name"] == "controller":
                        field["value"] = "<none>"
                    if field["name"] == "supervisor":
                        field["value"] = False
            if node["name"] == "MingMou" and node["DEF"] == "Mingmou":
                my_log.info("找到明眸节点")
                has_controller = False
                has_supervisor = False
                for field in node["fields"]:
                    # if "controller" not in node["fields"]:

                    # else:
                    if field["name"] == "controller":
                        my_log.info("有controller字段，修改")
                        field["value"] = controller_type
                        has_controller = True
                        my_log.info("设置明眸handle_wbt_file %s", field["value"])

                    if field["name"] == "supervisor":
                        my_log.info("有supervisor字段，修改")
                        has_supervisor = True
                        field["value"] = True

                if has_controller == False:
                    my_log.info("没有controller字段，创建")
                    node["fields"].append(
                        {
                            "name": "controller",
                            "type": "SFString",
                            "value": controller_type,
                        }
                    )
                    my_log.info("Create and handle_wbt_file %s", controller_type)

                if has_supervisor == False:
                    my_log.info("没有supervisor字段，创建")
                    node["fields"].append({"name": "supervisor", "type": "SFBool", "value": True})

        wp.save(start_wbt_file)

    @staticmethod
    def stop_docker():
        subprocess.run(['docker', 'stop', 'vnsim_dev'])
        subprocess.run(["docker", "rm", "vnsim_dev"])
        my_log.info("停止容器vnsim_dev")

    def delete_copy_wbt(self):
        for wbt in self.controller_wbt_lst:
            os.remove(wbt['wbt_file'])
            os.remove(wbt['wbproj_file'])
            my_log.info(f"File deleted successfully to {wbt['wbt_file']}，{wbt['wbproj_file']}")


def stop_all_docker():
    result = subprocess.run("docker ps -q", shell=True, capture_output=True, text=True)
    container_ids = result.stdout.strip().splitlines()
    if container_ids:
        subprocess.run("docker stop $(docker ps -q)", shell=True)
    my_log.info("停止所有容器")


if __name__ == "__main__":
    docker_file = r"/home/visionnav/VNSim/vnsimautotest/startDockerAutoTest.sh"
    wbt_file = r"/home/visionnav/VNSim/vn_wbt_project/auto_test/detect_put_p.wbt"
    dw_obj = DockerWbt(wbt_file, flag_start_with_bright_eye=False)
    dw_obj.load(dw_obj.wbt_file)
    dw_obj.get_controller_wbt_lst()
    dw_obj.prepare_wbt_file()
    dw_obj.start_docker(docker_file)
    # stop_all_docker()