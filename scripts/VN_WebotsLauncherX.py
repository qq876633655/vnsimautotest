import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import time
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from webots_parser import WebotsParser

__version__ = "5.2.0.13-lgc"


class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.moveCursor(self.text_widget.textCursor().End)
        self.text_widget.insertPlainText(msg + "\n")
        self.text_widget.ensureCursorVisible()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_name = None
        self.file_name_copy = []
        self.controller_list = []
        self.wbts = None

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建顶部按钮组
        top_buttons_layout = QHBoxLayout()
        self.instructions_button = QPushButton(
            QIcon("instructions_icon.png"), "点我！必看！使用说明", self
        )
        # 将按钮添加到顶部按钮组
        top_buttons_layout.addWidget(self.instructions_button)

        # 创建下拉框和标签
        combo_layout = QHBoxLayout()
        self.open_button = QPushButton(QIcon("open_icon.png"), "必选！wbt文件", self)
        self.label_wbt = QLabel("未选择wbt文件", self)
        combo_layout.addWidget(self.open_button)

        self.edit_button = QPushButton(QIcon("start_icon.png"), "场景编辑", self)

        # 操作按钮
        self.start_button = QPushButton(QIcon("start_icon.png"), "启动", self)
        self.stop_button = QPushButton(QIcon("stop_icon.png"), "关闭", self)
        self.stop_button_force = QPushButton(
            QIcon("stop_icon_force.png"), "强制关闭", self
        )

        # 创建一个 QCheckBox
        self.start_with_bright_eye = QPushButton(
            QIcon("restart_icon.png"), "带明眸启动", self
        )
        # self.restart_button = QPushButton(QIcon("restart_icon.png"), "重启", self)

        # 操作按钮区域
        manipulate_layout = QHBoxLayout()
        manipulate_layout.addWidget(self.start_button)
        manipulate_layout.addWidget(self.stop_button)
        manipulate_layout.addWidget(self.stop_button_force)
        manipulate_layout.addWidget(self.start_with_bright_eye)
        # manipulate_layout.addWidget(self.restart_button)

        # 增加一个版本号显示区域
        self.version_label = QLabel(f"版本号：{__version__}", self)
        # 创建一个 QPushButton
        self.copy_button = QPushButton("复制版本号", self)
        version_layout = QHBoxLayout()
        version_layout.addWidget(self.version_label)
        version_layout.addWidget(self.copy_button)

        # 日志输出区域
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)

        # 设置日志记录器
        log_handler = LogHandler(self.log_output)
        qtlog_formatter = logging.Formatter(
            "[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_handler.setFormatter(qtlog_formatter)
        logger.addHandler(log_handler)

        # 将各部分添加到主布局
        main_layout.addLayout(top_buttons_layout)
        main_layout.addLayout(combo_layout)
        main_layout.addWidget(self.label_wbt)
        main_layout.addWidget(self.edit_button)
        main_layout.addLayout(manipulate_layout)
        main_layout.addWidget(self.log_output, stretch=1)
        main_layout.addLayout(version_layout)

        # 设置样式
        self.setStyleSheet(
            """
            QPushButton {
                font-size: 14px;
                padding: 8px 16px;
                margin: 5px;
            }
            QLabel {
                font-size: 14px;
            }
            QTextEdit {
                font-size: 14px;
                border: 1px solid #ccc;
                padding: 8px;
            }
        """
        )

        # 设置主布局
        self.setLayout(main_layout)
        self.setWindowTitle("VN_Webots启动器")
        # self.setGeometry(300, 300, 900, 400)

        # 其他初始化代码...
        self.instructions_button.clicked.connect(self.showInstructions)
        self.open_button.clicked.connect(self.onOpenWbtClick)
        self.start_button.clicked.connect(self.onStartClick)
        self.stop_button.clicked.connect(self.onStopClick)
        self.stop_button_force.clicked.connect(self.onStopForceClick)
        # self.restart_button.clicked.connect(self.onRestartClick)
        self.start_with_bright_eye.clicked.connect(self.onStartClickWithBrightEye)
        self.edit_button.clicked.connect(self.onEditClick)
        # 连接按钮的点击事件到槽函数
        self.copy_button.clicked.connect(self.copy_text)

    def showInstructions(self):
        """
        显示使用说明的对话框，使用HTML格式。
        """
        html_msg = (
            "<h3>使用说明</h3>"
            "<ol>"
            "<li><strong>常规使用：</strong>选择wbt文件后，点击“启动”按钮，既可使用拉起仿真系统的程序。</li>"
            "<li><strong>文件处理：</strong>启动器复制wbt文件并以此启动Webots，运行时直接修改不保存。如需修改，需使用“场景编辑”功能对wbt进行修改,修改后重启生效。</li>"
            "<li><strong>关闭功能：</strong>仅关闭由启动器启动的Webots实例。</li>"
            "<li><strong>强制关闭：</strong>终止所有Webots进程。</li>"
            "<li><strong>状态重置：</strong>启动器启动的wbt将重置至初始状态。</li>"
            "</ol>"
        )
        QMessageBox.information(self, "使用说明", html_msg)

    def onOpenWbtClick(self):
        # Todo: 优化初始路径
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "必选！wbt文件", "", "所有文件 (*);;文本文件 (*.txt)", options=options
        )
        # 如果文件名后缀不是.wbt，则报请选择wbt文件及提示
        if not self.file_name:
            logger.warning("您未选择文件，请选择wbt文件")
            self.label_wbt.setText(f"未选择wbt文件")
            return
        elif not self.file_name.endswith(".wbt"):
            self.file_name = None
            logger.warning("该文件不是wbt文件，请选择wbt文件")
            self.label_wbt.setText(f"未选择wbt文件")
        else:
            wbtc = WbtChecker(self.file_name)
            wbtc.get_Robot_controller_list()
            self.controller_list = wbtc.controller_list
            logger.info(f"init {self.controller_list} ")
            self.label_wbt.setText(f"选择了：{self.file_name} ")

    def onEditClick(self):
        if self.file_name:
            if self.wbts != None:
                self.onStopClick()
            prosess_edit = subprocess.Popen(["webots", "--mode=pause", self.file_name])
        else:
            logger.warning("请选择wbt文件")

    def onStartClick(self, flag_start_with_bright_eye=False):
        if self.file_name and self.controller_list:
            self.wbts = WbtProcessParallel(
                self.file_name, self.controller_list, flag_start_with_bright_eye
            )
            self.wbts.run()
            logger.info(f"启动完毕")
        else:
            logger.warning("请选择wbt文件或确认robot配置")

    def onStartClickWithBrightEye(self):
        self.onStartClick(flag_start_with_bright_eye=True)

    def onStopClick(self):
        if self.wbts == None:
            logger.warning("请先用启动器启动wbt")
            return
        else:
            try:
                self.file_name_copy = self.wbts.start_wbt_list
                self.wbts.stop_all_wbt()
                logger.info(f"停止所有wbt: {self.file_name}")
                self.wbts = None
            except Exception as e:
                logger.error(f"Try to stop wbt: {e}")

            # 删除拷贝后的文件，1.检查文件或目录是否存在
            for copyed_file in self.file_name_copy:
                if os.path.exists(copyed_file):
                    try:
                        os.remove(copyed_file)
                        logger.info(f"删除拷贝后的文件: {copyed_file}")
                    except Exception as e:
                        # 提高了异常的捕获范围，并给出更有用的反馈
                        logger.error(
                            f"Error executing delete command for {copyed_file}: {e}"
                        )
                else:
                    # 如果文件不存在，给出友好的提示
                    logger.warning(f"File {copyed_file} does not exist.")

    def onStopForceClick(self):
        # 使用更加安全的命令执行方式，并确保命令执行的正确性
        try:
            # 查询webots进程，这里保持使用列表传递参数，因为没有外部输入，所以相对安全
            subprocess.run(
                ["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # 终止webots进程，并捕获可能的异常
            result = subprocess.run(["killall", "webots"])
            if result.returncode != 0:
                logger.error(
                    f"未能终止webots进程，错误码：{result.returncode}。错误码：1，表示无webots进程。"
                )
                return
        except Exception as e:
            logger.error(f"操作过程中发生错误：{e}")
            return

        # 此处日志记录放在确认进程终止之后，确保操作已完成
        logger.info(f"停止所有wbt进程")

    def onRestartClick(self):
        if self.wbts == None:
            logger.warning("请先用启动器启动wbt")
            return
        else:
            self.onStopClick()
            self.onStartClick()

    def closeEvent(self, event):
        self.onStopClick()
        logger.info("closeEvent")

    def copy_text(self):
        # 获取系统剪贴板
        clipboard = QApplication.clipboard()

        # 将文本复制到剪贴板
        clipboard.setText(__version__)

        logger.warning(f"版本号{__version__}信息复制成功")


class WbtProcessParallel:
    def __init__(self, wbt_file, controller_list, flag_start_with_bright_eye=False):
        self.process = []
        self.wbt_file = wbt_file
        self.controller_list = controller_list
        if flag_start_with_bright_eye:
            if "shadow_be" not in self.controller_list:
                self.controller_list.insert(len(self.controller_list) - 2, "shadow_be")
            logger.info(f"start with bright eye")
        self.cpu_num = [0, 2, 3, 4, 5]
        print(self.controller_list)
        self.start_wbt_list = []
        self.prepare_wbt_file()

    def prepare_wbt_file(self):
        for index, controller_type in enumerate(self.controller_list):
            print(index, controller_type)
            # to-do :prepare .wbproj
            destination_wbt = self.wbt_file.replace(
                ".wbt", controller_type + "_VN_WebotsLauncherX_copy.wbt"
            )
            try:
                shutil.copy(self.wbt_file, destination_wbt)
                logger.info(f"File copied successfully to {destination_wbt}")
                self.start_wbt_list.append(destination_wbt)
            except FileExistsError:
                logger.error("wbt_file does not exit.")
            except PermissionError:
                logger.error("Permision denied for the wbt_file")
            except Exception as e:
                logger.error(f"An error occurred: {e}")

            if "gui" in controller_type:
                dir_name, file_name = os.path.split(destination_wbt)
                newfile_name = file_name.replace(".wbt", ".wbproj")
                wbproj_file = os.path.join(dir_name, "." + newfile_name)
                self.create_wbproj_with_SimulationView(wbproj_file)
            else:
                dir_name, file_name = os.path.split(destination_wbt)
                newfile_name = file_name.replace(".wbt", ".wbproj")
                wbproj_file = os.path.join(dir_name, "." + newfile_name)
                self.create_wbproj_without_SimulationView(wbproj_file)

    def create_wbproj_without_SimulationView(self, wbproj_file):
        print(wbproj_file)
        with open(wbproj_file, "w") as file:
            file.write("Webots Project File version R2024a\ncentralWidgetVisible: 0\n")

        print(f"create_wbproj_without_SimulationView '{wbproj_file}' 已被处理。")

    def create_wbproj_with_SimulationView(self, wbproj_file):
        print(wbproj_file)
        with open(wbproj_file, "w") as file:
            file.write("Webots Project File version R2024a\ncentralWidgetVisible: 1\n")

        print(f"create_wbproj_without_SimulationView '{wbproj_file}' 已被处理。")

    def run(self):
        for index, controller_type in enumerate(self.controller_list):
            # time.sleep(2)
            if "gui" in controller_type:
                self.handle_wbt_file(self.start_wbt_list[index], controller_type)
                time.sleep(1)
                try:
                    print(
                        "webots",
                        "--mode=realtime",
                        self.start_wbt_list[index],
                    )
                    prosess_gui = subprocess.Popen(
                        [
                            "webots",
                            "--mode=realtime",
                            self.start_wbt_list[index],
                        ]
                    )
                    self.process.append(prosess_gui)
                except Exception as e:
                    logger.error(f"Error starting Webots: {e}")

            else:
                if "shadow_be" in controller_type:
                    self.handle_wbt_file_for_bright_eye(
                        self.start_wbt_list[index], controller_type
                    )
                else:
                    self.handle_wbt_file(self.start_wbt_list[index], controller_type)
                time.sleep(1)
                if "master" in controller_type:
                    try:
                        print(
                            "taskset",
                            "-c",
                            str(self.cpu_num[index])+","+str(self.cpu_num[index]+1),
                            "webots",
                            "--mode=realtime",
                            "--no-rendering",
                            self.start_wbt_list[index],
                        )
                        prosess_others = subprocess.Popen(
                            [
                                "taskset",
                                "-c",
                                str(self.cpu_num[index])+","+str(self.cpu_num[index]+1),
                                "webots",
                                "--mode=realtime",
                                "--no-rendering",
                                "--minimize",
                                self.start_wbt_list[index],
                            ]
                        )
                        self.process.append(prosess_others)
                    except Exception as e:
                        logger.error(f"Error starting Webots: {e}")
                else:
                    try:
                        print(
                            "taskset",
                            "-c",
                            str(self.cpu_num[index]),
                            "webots",
                            "--mode=realtime",
                            "--no-rendering",
                            self.start_wbt_list[index],
                        )
                        prosess_others = subprocess.Popen(
                            [
                                "taskset",
                                "-c",
                                str(self.cpu_num[index]),
                                "webots",
                                "--mode=realtime",
                                "--no-rendering",
                                "--minimize",
                                self.start_wbt_list[index],
                            ]
                        )
                        self.process.append(prosess_others)
                    except Exception as e:
                        logger.error(f"Error starting Webots: {e}")
                        

    def handle_wbt_file(self, start_wbt_file, controller_type):
        wp = WebotsParser()
        wp.load(start_wbt_file)

        for node in wp.content["root"]:
            if node["name"] == "ConvoyerBelt":
                for field in node["fields"]:
                    if field["name"] == "controller" and "master" in controller_type:
                        field["value"] = "ConvoyerRobot"
                        logger.info("修改ConvoyerBelt的controller为ConvoyerRobot %s", controller_type)
            if node["name"] == "Robot" and node["DEF"] == "RobotNode":
                for field in node["fields"]:
                    if field["name"] == "controller":
                        field["value"] = controller_type
                        logger.info("handle_wbt_file %s", field["value"])

        wp.save(start_wbt_file)

    def handle_wbt_file_for_bright_eye(self, start_wbt_file, controller_type):
        logger.info("启动明眸")
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
                logger.info("找到明眸节点")
                has_controller = False
                has_supervisor = False
                for field in node["fields"]:
                    # if "controller" not in node["fields"]:

                    # else:
                    if field["name"] == "controller":
                        logger.info("有controller字段，修改")
                        field["value"] = controller_type
                        has_controller = True
                        logger.info("设置明眸handle_wbt_file %s", field["value"])

                    if field["name"] == "supervisor":
                        logger.info("有supervisor字段，修改")
                        has_supervisor = True
                        field["value"] = True

                if has_controller == False:
                        logger.info("没有controller字段，创建")
                        node["fields"].append(
                            {
                                "name": "controller",
                                "type": "SFString",
                                "value": controller_type,
                            }
                        )
                        logger.info("Create and handle_wbt_file %s", controller_type)

                if has_supervisor == False:
                        logger.info("没有supervisor字段，创建")
                        node["fields"].append({"name": "supervisor", "type": "SFBool", "value": True})


        wp.save(start_wbt_file)

    def stop_all_wbt(self):
        print(len(self.process))
        for process in self.process:
            process.terminate()


class WbtChecker:
    def __init__(self, wbt_file):
        self.wp = WebotsParser()
        self.wp.load(wbt_file)
        self.controller_list = []
        # self.get_Robot_controller_list()

    def check_world_info(self):
        for node in self.wp.content["root"]:
            if node["name"] == "WorldInfo":
                for field in node["fields"]:
                    print(field)
                print((node.get("fields")))
                # print( node.get("fields")["physicsDisableTime"])
                # assert node["fields"]["basicTimeStep"] == 10
                # assert node["fields"]["FPS"] == 10
                # assert node["fields"]["physicsDisableTime"] == 0

                # print(node)
                # if node['DEF'] == 'RobotNode':

                if "controllerProperties" in node:
                    print("ok")

    def get_Robot_controller_list(self):
        for node in self.wp.content["root"]:
            if node["name"] == "Robot":
                if node["DEF"] == "RobotNode":
                    for field in node["fields"]:
                        if field["name"] == "customData":
                            customData_str = field["value"]
                            logger.info(
                                "Robot RobotNode customData_str: %s ", customData_str
                            )
                            # return customData_str
                            # 使用正则表达式匹配括号内的内容
                            match = re.search(
                                r"controller_list\[(.*?)\]", customData_str
                            )
                            if match:
                                # 获取匹配的内容
                                content = match.group(1)
                                # 将内容按逗号分割，然后添加到列表中
                                self.controller_list = content.split(",")
                            else:
                                logger.error(
                                    "Can't match controoler_list from Robot_customData"
                                )
                            return


def vn_assets_unzip():
    folder_path = "/home/visionnav/.vn_simulation"
    assets_path = "/home/visionnav/.vn_simulation/vn_wbt_assets"
    assets_zip_path = "/home/visionnav/vn_wbt_assets.zip"
    # 检查folder_path文件夹是否存在
    if os.path.exists(assets_path) and os.path.isdir(assets_path):
        logger.info("vn_wbt_assets文件存在")

    else:
        logger.info("vn_wbt_assets文件不存在，运行解压程序")
        # 运行解压程序
        pass_word = "vn_simulation"
        try:
            cmd = ["unzip", "-P", pass_word, assets_zip_path, "-d", folder_path]
            prosess_unzip = subprocess.Popen(cmd)
            # while True:
            #     stdout,stderr = prosess_unzip.communicate()
            #     returncode = prosess_unzip.returncode
            #     if returncode == 0:
            #         print("解压程序，执行成功！")
            #     if stdout == '' and p.poll() != None:
            #         break
        except Exception as e:
            logger.error(f"解压程序，出错！错误信息： {str(e)}")


def set_assets_path():
    pass


if __name__ == "__main__":

    # 修改日志文件路径
    log_dir = "/home/visionnav/logs/simulaite_assistant"
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Failed to create log directory: {e}")

    log_file_path = os.path.join(log_dir, "simulaite_assistant.log")
    log_file_path = os.path.abspath(log_file_path)

    # 设置日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 设置日志文件的参数
    max_size = 10 * 1024 * 1024  # 设置日志文件的最大大小为10MB
    backup_count = 20  # 设置日志文件的最大备份数量为20

    handler = RotatingFileHandler(
        log_file_path, maxBytes=max_size, backupCount=backup_count
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # vn_assets_unzip()
    #
    # app = QApplication(sys.argv)
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # icon_path = os.path.join(current_dir,"VNsim.png")
    # icon = QIcon(icon_path)
    # app.setWindowIcon(icon)
    # ex = MyApp()
    # ex.show()
    # sys.exit(app.exec_())
    # pid = subprocess.Popen(['webots', '--mode=realtime', '/home/visionnav/VNSim/vn_wbt_project/auto_test/world/detect_get_p.wbt'])
    # time.sleep(30)
    # pid.terminate()

    # 单独测试WbtProcess
    handler = WbtProcessParallel('/home/visionnav/vn_wbt_project/auto_test/world/detect_get_p.wbt',
                                 ['P15_master','shadow_lidar0_and_lidar2','shadow_lidar1','shadow_lidar3_and_lidar4','P15_shadow_sensor','shadow_show_gui',])
    # ['P15_master', 'shadow_lidar0_and_lidar2', 'shadow_lidar1', 'shadow_lidar3_and_lidar4', 'P15_shadow_sensor',
    #  'shadow_show_gui']
    # handler.stop_all_wbt()
    handler.run()
    # import time
    # time.sleep(30)
    # handler.stop_all_wbt()

    # 单独测试WbtChecker
    # 获取当前文件路径
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # wbt_checker = WbtChecker(
    #     current_dir+"/../test/JPN2023118_P15_Switch.wbt"
    # )
    # wbt_checker.check_world_info()
    # wbt_checker.get_Robot_controller_list()
    # print(wbt_checker.controller_list)