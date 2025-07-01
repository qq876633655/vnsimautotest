# -*- coding: utf-8 -*-
"""
Time:2023/7/15 13:35
Author:yanglei
File:perceptionpro_cfg.py
"""

# 开发环境
ENV = 'dev'

# 数据库名称
PER_DB_NAME = 'test_platform_dev'

# 数据库地址
PER_DB_HOST = '10.20.20.57'

# 平台版本
PERPRO_VERSION = '1.1.8'

# 现场问题是否打开自动记录到 jira
IS_ONSITE_ISSUES_JIRA = False

# 现场问题是否发送钉钉通知
IS_ONSITE_ISSUES_DD = True

# 感知版本发布是否发送钉钉通知
DD_VERSIONS = True

# 定位版本发布是否发送钉钉通知
LOC_DD_VERSIONS = True

# 控制版本发布是否发送钉钉通知
CTL_DD_VERSIONS = True

# 现场问题需要的数据文件
ONSITE_ISSUES_ATTACHMENT_LST = ["AGVPerceptionModule.config", "Cards.config", "Cards_2D.config", "config_mid360.config",
                                "cpp.log.config", "cpp.log_2D.config", "ErrorCode_2D.config",
                                "ForkingPerception_2D.config", "LaserChannels_2D.config", "LaserChannels3D.config",
                                "BrightEyes.config", "parks.config", "SensorsInfo.config", "Cameras.config",
                                "StorageMonitor.config"]
# 定位现场问题需要的config文件
LOC_ONSITE_ISSUES_ATTACHMENT_LST = [
    "cpp.multilingual.config", "cpp_vn3D_localization.log.config", "LocalParam.config", "mid_360.json",
    "MultiLidar.yaml"
]

# 现场问题 jira 服务器地址
ONSITE_ISSUES_JIRA_SERVER_URL = r"http://61.144.219.234:8090/browse/"

# 测试用的钉钉群机器人 secret webhook
TEST_SECRET = "SEC523a1e582932bb5c3eb113a45b6b98f426481558e33dd936dc7898be707fcc6f"
TEST_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=1efeb076d79f829191905aaab989fcdb87bfb" \
               "fccbc106d721d6891d9ddba4502"

# 感知现场问题钉钉群机器人 secret webhook
ONSITE_ISSUES_SECRET = 'SEC800419863b6d23343e82b86ea8b9eac1569b800a064e8b7e3d9fc96d923a073f'
ONSITE_ISSUES_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=db3aeea3a20092d697cb5ab267cd" \
                        "470bf330dffa68534d6d7f0e4370189e5cb6"

# 感知版本发布钉钉V4项目群机器人 secret webhook
V4_VERSIONS_SECRET = "SEC40df609231f1da2bea5ce5ab13d2643fabd6c85c5b751cf8f38f4a3a4ed96186"
V4_VERSIONS_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=da5b572f23560bfe1b0c4b10c7481d7a1" \
                      "000e12755be3051757a5ad31a2ee574"

# 感知版本发布钉钉PD2226项目群机器人 secret webhook
PD2226_VERSIONS_SECRET = "SECab403d040e0843b0613b95fa5804531c2003f2fe1237ebc929838be9c63ab9ea"
PD2226_VERSIONS_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=897aee3c4475f787bfea9aff82923b" \
                          "4e3ab976c7edd4f36e295377596491c1e0"

# 感知版本发布通知人
VERSIONS_AT_MOBILES = ['18325815905', '17666076037', '17841711172', '15889657591', '13232121012', '16679001203',
                       '19960803450']

# PerPro 内网服务地址
PER_PRO_LOCAL_SERVER_URL = r"http://10.20.20.57:7898"

# PerPro 外网服务地址
PER_PRO_GLOBAL_SERVER_URL = r"http://61.190.73.83:7898"

# 定位版本发布通知人
LOC_VERSIONS_AT_MOBILES = ['18325815905', '15526429137', '15052720065']

# 定位版本发布钉钉V4项目群机器人 secret webhook
LOC_VERSIONS_SECRET = "SECcf0b10851f56303b74e5f9f36d469fd338c1db1e5b281b577bf18700651553f2"
LOC_VERSIONS_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=a197324df832c5cbc8a8a6b72fb72ded1c320" \
                       "4504209355e19cda41e43589167"

# 定位现场问题测试机器人   secret webhook
LOC_ONSITE_SECRET = "SECf5c5fcb96902e034461b59a11a93ab9902ac795963cbbb2b47cfaba092c28f3a"
LOC_ONSITE_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=fe5698e0e2f4f302a98aced3f8c689670652ab96385ce70ac6a5c43e2b35f4bd"

# 测试机器人现场问题   secret webhook
DD_TEST_SECRET_CXY = "SEC4e5a330000fbbaedd5b65b1cf51ff33ebbc7bee40ba8375aff3803cd497a354d"
DD_TEST_WEBHOOK_CXY = "https://oapi.dingtalk.com/robot/send?access_token=9ff527c28e4d22c0beb0025f995a986d7a86acb8af129d0cc852f348d272cf26"

# 仿真启动脚本地址
SIM_ENV = "/home/visionnav/webots/plugins/tray_simulation"

# 感知仓库地址，必须在服务器中存在
PER_REPO_PATH = "/home/visionnav/code/verticalservoperception"

# 感知 so 名称，看编译感知的服务器 python 版本
PER_SO = 'perception.cpython-38-x86_64-linux-gnu.so'

# 感知 so 存放在感知仓库中的地址
BUILD_PER_SO = 'build/lib.linux-x86_64-3.8/perception.cpython-38-x86_64-linux-gnu.so'

# 通知仿真完成的 secret webhook
SIM_RESULT_SECRET = "SEC19c141a55c4f6f2dc9f4243abfe6ba6260de6fb63e8af0080155ae857c44290f"
SIM_RESULT_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=c872cbc3fe5f010bd19b1693ae4f6279a232c350ec3cace1bacef25d00e659d3"

# 控制版本发布钉钉机器人 secret webhook
CTL_VERSIONS_SECRET = "SEC4ea83105207ef75b4e7bd2d56ac90608d2bd608797913a12182298001331a6a0"
CTL_VERSIONS_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=f718d2827eda0eca976e255129563f7b2601aa7c199dbf705ced6ad222b1b56b"

# 控制测试人员
CTL_VERSIONS_AT_MOBILES = ['18325815905', '15526429137', '13430166941']

# general server 版本发布是否发送钉钉通知
GF_DD_VERSIONS = False

# general server 版本发布钉钉机器人 secret webhook
GF_VERSIONS_SECRET = ""
GF_VERSIONS_WEBHOOK = ""

# general server 测试人员
GF_VERSIONS_AT_MOBILES = []

# robotune 版本发布是否发送钉钉通知
RB_DD_VERSIONS = False

# robotune 版本发布钉钉机器人 secret webhook
RB_VERSIONS_SECRET = ""
RB_VERSIONS_WEBHOOK = ""

# robotune 测试人员
RB_VERSIONS_AT_MOBILES = []

# 仿真调试
SIM_TEST_DEBUG = True

# 微应用配置
corp_id = "ding93a88f01dc7a5a8735c2f4657eb6378f"

# 钉钉H5微应用开发环境——CXY
DD_TEST_APPLICATION_TEST_APP_KEY_CXY = "dingpnqfrvzg80dbuevb"
DD_TEST_APPLICATION_TEST_APP_SECRET_CXY = "cwjcTQZsgCeU-MWvLUYyOMCPVLgNQXTecfVrdrM1_r2myDISdwQAXZ5wxGLw3yQO"

# 测试版钉钉机器人，微应用
ROBOT_CODE_TEST_CXY = "dingpnqfrvzg80dbuevb"

# 发布版H5微应用生产环境
DD_H5_APPLICATION_CLIENT_ID = "dingnnpn4oajxevomvwj"
DD_H5_APPLICATION_CLIENT_SECRET = "9wtNb4ogG4ndA680DhLxdnsSKBy2ZPaku5LdsiJl7XqgRZGNUG_z05ud8aWE_faP"

# 发布版H5微应用钉钉机器人
ROBOT_CODE = "dingnnpn4oajxevomvwj"

# sensor 版本发布是否发送钉钉通知
SEN_DD_VERSIONS = True

# sensor 版本发布钉钉机器人 secret webhook
SEN_VERSIONS_SECRET = "SECe4d4604d03ac7cc26407329d2db50802d4d449766b831ba90023777bf5d59016"
SEN_VERSIONS_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=1f11a13e3ee66cfc494302ba7d5c305c61dc0059c76e1d3417abd3e001007ee3"

# sensor 测试人员
SEN_VERSIONS_AT_MOBILES = ['18325815905', '16679001203']

# lyang发布版H5微应用生产环境
DD_YL_H5_APPLICATION_CLIENT_ID = "dingntydfi1xlippalms"
DD_YL_H5_APPLICATION_CLIENT_SECRET = "tnoP1sjoamPGSId72oeeRRn69Yvhb_NaaF7J1cw9PQ8rwHSXdvjuDqO8JDvw53uB"

# lyang发布版H5微应用钉钉机器人
ROBOT_CODE_TEST_YL = "dingntydfi1xlippalms"

# robotune地址
ROBOTUNE_ADDR = "http://10.20.20.179:8090/scene/home"
