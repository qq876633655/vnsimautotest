# -*- coding: utf-8 -*-

import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import time
import shutil
from scripts.webots_parser import WebotsParser
from src.log import my_log


class DockerWbt(WebotsParser):
    def __init__(self, wbt_file, flag_start_with_bright_eye=False):
        super().__init__()
        self.process = []
        self.wbt_file = wbt_file
        self.flag_start_with_bright_eye = flag_start_with_bright_eye
        self.cpu_num = [0, 2, 3, 4, 5]
        self.controller_wbt_lst = []

    def check_wbt(self):
        try:
            self.load(self.wbt_file)
        except BaseException as e:
            my_log.error(f'加载 wbt 有问题：{e}')

    def get_robot_controller_list(self):
        try:
            for node in self.content["root"]:
                if node["name"] == "Robot":
                    if node["DEF"] == "RobotNode":
                        for field in node["fields"]:
                            if field["name"] == "customData":
                                customData_str = field["value"]
                                match = re.search(
                                    r"controller_list\[(.*?)\]", customData_str
                                )
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
                                    my_log.error("没有匹配到控制器列表")
        except BaseException as e:
            my_log.error(f'获取控制器列表异常：{e}')

    def prepare_wbt_file(self, controller_wbt_lst):
        """
        处理 wbt 配置文件 centralWidgetVisible: 1 显示中央主窗口 0 关闭中央主窗口
        :return:
        """
        for wbt in controller_wbt_lst:
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

    def delete_wbt_file(self, controller_wbt_lst):
        for wbt in controller_wbt_lst:
            os.remove(wbt['wbt_file'])
            os.remove(wbt['wbproj_file'])
            my_log.info(f"File deleted successfully to {wbt['wbt_file']}，{wbt['wbproj_file']}")

    def run(self):
        for index, controller_type in enumerate(self.controller_list):
            # time.sleep(2)
            if "gui" in controller_type:
                self.handle_wbt_file(self.start_wbt_list[index], controller_type)
                time.sleep(1)
                prosess_gui = subprocess.Popen(["webots","--mode=realtime",self.start_wbt_list[index],])
                self.process.append(prosess_gui)
            else:
                if "shadow_be" in controller_type:
                    self.handle_wbt_file_for_bright_eye(self.start_wbt_list[index], controller_type)
                else:
                    self.handle_wbt_file(self.start_wbt_list[index], controller_type)
                time.sleep(1)
                if "master" in controller_type:
                    prosess_others = subprocess.Popen(
                        ["taskset","-c",str(self.cpu_num[index]) + "," + str(self.cpu_num[index] + 1),
                            "webots","--mode=realtime","--no-rendering","--minimize",self.start_wbt_list[index],])
                    self.process.append(prosess_others)
                else:
                    try:
                        prosess_others = subprocess.Popen(
                            ["taskset","-c",str(self.cpu_num[index]),"webots","--mode=realtime","--no-rendering",
                                "--minimize",self.start_wbt_list[index],]
                        )
                        self.process.append(prosess_others)
                    except Exception as e:
                        my_log.error(f"Error starting Webots: {e}")

    def handle_wbt_file(self, start_wbt_file, controller_type):
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
                        my_log.info(f"handle_wbt_file：{field['value']}", )
        wp.save(start_wbt_file)

    def handle_wbt_file_for_bright_eye(self, start_wbt_file, controller_type):
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

    def stop_all_wbt(self):
        print(len(self.process))
        for process in self.process:
            process.terminate()


if __name__ == "__main__":
    wbt_file = r"/home/visionnav/VNSim/vn_wbt_project/auto_test/detect_get_p.wbt"
    dw = DockerWbt(wbt_file, False)
    dw.check_wbt()
    dw.get_robot_controller_list()
    dw.prepare_wbt_file(dw.controller_wbt_lst)
    # for i in dw.controller_wbt_lst:
    #     dw.handle_wbt_file(i['wbt_file'], i['controller_type'])
    # dw.delete_wbt_file(dw.controller_wbt_lst)


