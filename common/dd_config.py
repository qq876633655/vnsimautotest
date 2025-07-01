#!/user/bin/env python
# -*- conding:utf-8 -*-
"""
@author  :xychen
@date    :2024/6/18   16:25
@File    :dd_config.py
@Notes   :


"""
from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_dingtalk.robot_1_0.client import Client as dingtalkrobot_1_0Client
from alibabacloud_dingtalk.contact_1_0.client import Client as dingtalkcontact_1_0Client
from config import perceptionpro_cfg as ppc

def api2_1_0_config():
    """
    钉钉接口配置
    :return: 钉钉配置参数
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkoauth2_1_0Client(config)

def api1_0_config():
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkrobot_1_0Client(config)

def api1_0_client_config():
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkcontact_1_0Client(config)

#获取微应用的token方法
def get_app_access_token():
    """
    获取app_access_token
    :return: access token参数
    """
    if ppc.ENV == "dev":
        app_key = ppc.DD_TEST_APPLICATION_TEST_APP_KEY_CXY
        app_secret = ppc.DD_TEST_APPLICATION_TEST_APP_SECRET_CXY
    else:
        app_key = ppc.DD_H5_APPLICATION_CLIENT_ID
        app_secret = ppc.DD_H5_APPLICATION_CLIENT_SECRET
    get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(app_key=app_key,app_secret=app_secret)
    app_token_code = api2_1_0_config().get_access_token(get_access_token_request)
    return app_token_code.body.access_token

if __name__ == '__main__':
    print(get_app_access_token())