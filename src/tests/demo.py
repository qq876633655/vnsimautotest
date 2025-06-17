
import datetime
import os
from pathlib import Path
import shutil
import time
LOG_SOURCE_DIR = Path('/home/visionnav/log')
LOG_TARGET_BASE_DIR = Path('/home/visionnav/autotest')
CPU_CSV_DIR = Path('/home/visionnav/VNSim/luoguancong/csv')
FLAG_received = False

def save_agv_log(task_name,task_id):
    # 生成保存日志的日期
    # 安全地拼接路径
    save_log_path = LOG_TARGET_BASE_DIR / f"{task_name}_{task_id}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    path = [LOG_SOURCE_DIR,CPU_CSV_DIR]
    # 记录日志

    # 复制日志目录
    for i in path:
        shutil.copytree(i, save_log_path,dirs_exist_ok=True)

if __name__ == '__main__':
    save_agv_log("test",1)
