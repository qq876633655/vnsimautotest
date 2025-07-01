import requests
import time
import datetime
# # 查询流程
# print(requests.get("http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo").json()["report"]["name"])

# requests.post("http://127.0.0.1:24311/api/services/task/DynamicFlow/ClearExistTask")

# # # 查询流程
# if requests.get("http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo").json()["report"] == None:
#     print("当前没有任务")
# else:
#     print("当前任务为：", requests.get("http://127.0.0.1:24311/api/services/task/Agv/GetCurrentTaskInfo").json()["report"]["name"])

# 获取异常流程面板

import requests
import datetime
import time

def timestamp_to_formatted_time(timestamp):
    """
    将时间戳（毫秒）转换为格式化的时间字符串（精确到毫秒）
    """
    error_sec = timestamp // 1000
    error_ms = timestamp % 1000
    dt_object = datetime.datetime.fromtimestamp(error_sec)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return f"{formatted_time}.{error_ms:03d}"

error_list = []
if not error_list:
    for i in range(3, 5):
        try:
            response = requests.get(f"http://127.0.0.1:24311/api/services/pm/WarningRecord/GetAll?Level={i}")
            response.raise_for_status()  # 检查请求是否成功
            items = response.json()["report"]["items"]
            for j in items:
                if (int(time.time() * 1000) - j["startTimestamp"]) / 1000 < 100000:
                    error_time = timestamp_to_formatted_time(j['startTimestamp'])
                    error_info = f"时间：{error_time} 错误码：{j['errorCode']} 错误信息：{j['warning']['name']} 错误等级：{j['level']} 错误模块：{j['serviceType']['serviceTypeName_zh']}"
                    error_list.append(error_info)
        except requests.RequestException as e:
            print(f"请求发生错误: {e}")
        except (KeyError, IndexError) as e:
            print(f"解析响应数据时发生错误: {e}")

with open('error_list.txt', 'w', encoding='utf-8') as f:
    for item in error_list:
        f.write(f"{item}\n")
    