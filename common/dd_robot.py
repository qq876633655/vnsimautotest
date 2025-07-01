# -*- coding: utf-8 -*-
"""
Time:2023/5/19 18:08
Author:yanglei
File:dd_robot.py
"""
import datetime
# https://oapi.dingtalk.com/robot/send?access_token=9ff527c28e4d22c0beb0025f995a986d7a86acb8af129d0cc852f348d272cf26
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

from common.log import my_log
from config import perceptionpro_cfg as ppc

from alibabacloud_dingtalk.robot_1_0 import models as dingtalkrobot__1__0_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from common import dd_config


def dd_webhook(secret, webhook):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    webhook += f"&timestamp={timestamp}&sign={sign}"
    return webhook


def send_message(payload, webhook):
    status = True
    response = requests.post(webhook, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
    if "ok" not in response.text:
        status = None
    return status


def onsite_issues_dd(summary, onsite_personnel, components, *at_mobile, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"概要：{summary}\n"
                       f"模块：{components}\n"
                       f"报告人：{onsite_personnel}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.ONSITE_ISSUES_SECRET, ppc.ONSITE_ISSUES_WEBHOOK)

    my_log.info(f"钉钉机器人_现场问题通知：{at_mobile}")
    return send_message(payload, webhook)


def loc_onsite_issues_dd(summary, issue_type, components, onsite_personnel, processing_type=None, *at_mobile,
                         is_at_all=False):
    if processing_type is None:
        payload = {
            "msgtype": "text",
            "text": {
                "content": f"概要：{summary}\n"
                           f"问题类型: {issue_type}\n"
                           f"模块：{components}\n"
                           f"报告人：{onsite_personnel}"
            },
            "at": {
                "atMobiles": at_mobile,
                "isAtAll": is_at_all
            },
        }
    else:
        payload = {
            "msgtype": "text",
            "text": {
                "content": f"概要：{summary}\n"
                           f"问题类型: {issue_type}\n"
                           f"模块：{components}\n"
                           f"报告人：{onsite_personnel}\n"
                           f"提示：时间已到期，请将({processing_type})状态切换"
            },
            "at": {
                "atMobiles": at_mobile,
                "isAtAll": is_at_all
            },
        }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.DD_TEST_SECRET_CXY, ppc.DD_TEST_WEBHOOK_CXY)
    else:
        webhook = dd_webhook(ppc.LOC_ONSITE_SECRET, ppc.LOC_ONSITE_WEBHOOK)

    my_log.info(f"钉钉机器人_现场问题通知：{at_mobile}")
    return send_message(payload, webhook)


def auto_test_dd(task_id, task_name, task_status, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.SIM_RESULT_SECRET, ppc.SIM_RESULT_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"任务id：{task_id}\n"
                       f"任务名称：{task_name}\n"
                       f"任务状态：{task_status}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_自动化测试完成通知：{task_id}")
    return send_message(payload, webhook)


def versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.V4_VERSIONS_SECRET, ppc.V4_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
        if versions_msg['apply_project'] == "st版本":
            del payload['at']
            webhook2 = dd_webhook(ppc.PD2226_VERSIONS_SECRET, ppc.PD2226_VERSIONS_WEBHOOK)
            status = send_message(payload, webhook2)
    my_log.info(f"钉钉机器人_感知版本发布通知：{versions_msg['versions']}")
    return status


def loc_versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/loc_versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.LOC_VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.LOC_VERSIONS_SECRET, ppc.LOC_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
    my_log.info(f"钉钉机器人_定位版本发布通知：{versions_msg['versions']}")
    return status


def ctl_versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/ctl_versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.CTL_VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.CTL_VERSIONS_SECRET, ppc.CTL_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
    my_log.info(f"钉钉机器人_控制版本发布通知：{versions_msg['versions']}")
    return status


def rb_versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/rb_versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.RB_VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.RB_VERSIONS_SECRET, ppc.RB_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
    my_log.info(f"钉钉机器人_新架构版本发布通知：{versions_msg['versions']}")
    return status


def gf_versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/gf_versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.GF_VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.GF_VERSIONS_SECRET, ppc.GF_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
    my_log.info(f"钉钉机器人_通用服务版本发布通知：{versions_msg['versions']}")
    return status


def versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.V4_VERSIONS_SECRET, ppc.V4_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


def ctl_versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.CTL_VERSIONS_SECRET, ppc.CTL_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


def loc_versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.LOC_VERSIONS_SECRET, ppc.LOC_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


def rb_versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.RB_VERSIONS_SECRET, ppc.RB_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


def gf_versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.GF_VERSIONS_SECRET, ppc.GF_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


# 钉钉H5微应用机器人
def dd_onsite_issues_robot(user_id, project_number, summary, status, personnel, agv_versions=None,
                           summary_problem=None) -> None:
    client = dd_config.api1_0_config()
    batch_send_otoheaders = dingtalkrobot__1__0_models.BatchSendOTOHeaders()
    batch_send_otoheaders.x_acs_dingtalk_access_token = dd_config.get_app_access_token()
    if summary_problem is None:
        msg_param = '{"content":' \
                    '"项目号：%s\n' \
                    '版本号：%s\n' \
                    '概要：%s\n' \
                    '状态：%s\n' \
                    '现场人员：%s\n' \
                    '"}' % (project_number, agv_versions, summary, status, personnel)
    else:
        msg_param = '{"content":"项目号：%s\n概要：%s\n状态：%s\n对接人：%s\n总结：%s\n"}' % (
        project_number, summary, status, personnel, summary_problem)
    if ppc.ENV == "dev":
        robot_code = ppc.ROBOT_CODE_TEST_CXY
    else:
        robot_code = ppc.ROBOT_CODE
    batch_send_otorequest = dingtalkrobot__1__0_models.BatchSendOTORequest(
        robot_code=robot_code,
        user_ids=[
            user_id
        ],
        msg_key='sampleText',
        msg_param=msg_param
    )
    try:
        client.batch_send_otowith_options(batch_send_otorequest, batch_send_otoheaders, util_models.RuntimeOptions())
        my_log.info(f"钉钉机器人_现场问题通知：{personnel}")
    except Exception as err:
        if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
            # err 中含有 code 和 message 属性，可帮助开发定位问题
            my_log.info(f"钉钉机器人_现场问题通知错误提示：", err)


def sen_versions_done_dd(versions, test_result, test_verdict, *at_mobile, is_at_all=False):
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(ppc.SEN_VERSIONS_SECRET, ppc.SEN_VERSIONS_WEBHOOK)
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions}\n"
                       f"测试结果：{test_result}\n"
                       f"测试总结：{test_verdict}"
        },
        "at": {
            "atMobiles": at_mobile,
            "isAtAll": is_at_all
        }
    }
    my_log.info(f"钉钉机器人_测试完成通知：{versions}")
    return send_message(payload, webhook)


def sen_versions_release_dd(versions_msg, creator, is_at_all=False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"版本号：{versions_msg['versions']}\n"
                       f"发版人：{creator}\n"
                       f"版本地址：\n{ppc.PER_PRO_GLOBAL_SERVER_URL}/media/sen_versions/{versions_msg['versions']}/{versions_msg['versions_file'].name}\n"
                       f"提测需求：\n{versions_msg['testing_requirements']}\n"
                       f"提测内容：\n{versions_msg['testing_content']}\n"
                       f"提测范围：\n{versions_msg['testing_range']}\n"
                       f"自测结果：\n{versions_msg['self_test_result']}"
        },
        "at": {
            "atMobiles": ppc.SEN_VERSIONS_AT_MOBILES,
            "isAtAll": is_at_all
        }
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
        status = send_message(payload, webhook)
    else:
        webhook1 = dd_webhook(ppc.SEN_VERSIONS_SECRET, ppc.SEN_VERSIONS_WEBHOOK)
        status = send_message(payload, webhook1)
    my_log.info(f"钉钉机器人_传感器版本发布通知：{versions_msg['versions']}")
    return status


if __name__ == '__main__':
    auto_test_dd(1, "test", '测试', '18325815905')
