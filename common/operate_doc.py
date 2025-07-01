# -*- coding: utf-8 -*-
"""
Time:2023/8/18 14:18
Author:yanglei
File:operate_doc.py
"""

import csv
import os
import re
import shutil
import time
from common.log import my_log


def create_file_copy(file_path, extension=None, copy=None):
    """
    创建文件的副本在文件目录下
    如果扩展名不一样，就不改变文件名
    如果扩展名一样，就在文件名后面 + 时间戳

    :param file_path: 文件绝对路径
    :param extension: 扩展名
    :param copy: 拷贝副本
    :return: 副本的绝对路径
    """
    dir_path = os.path.dirname(file_path)
    time_dst = time.strftime('%Y_%m_%d_%H_%M_%S')
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
    if extension:
        copy_file_name = f"{file_name}_{time_dst}{extension}"
    else:
        copy_file_name = f"{file_name}_{time_dst}{file_ext}"
    copy_file_path = os.path.join(dir_path, copy_file_name)
    if copy:
        shutil.copy(file_path, copy_file_path)
    return copy_file_path


def copy_file_content(file_path, number):
    """
    将文件内容复制多次到一个新文件中

    :param file_path: 文件地址
    :param number: 复制次数
    :return:
    """
    with open(file_path, 'r', encoding="UTF-8") as file:
        content = file.read()
    copied_content = content * number
    new_file_path = create_file_copy(file_path, copy=True)
    with open(new_file_path, 'w') as new_file:
        new_file.write(copied_content)
    print(f"文件内容已复制并写入新文件：{new_file_path}")


def get_first_end_timestamp(log_file):
    """
    获取日志文件中首行和尾行的时间戳

    :param log_file: 数据缓存
    :return:
    """
    lines = log_file.readlines()
    # 提取第一行时间戳
    first_line = lines[0].decode()
    first_timestamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', first_line).group(0)

    # 提取最后一行时间戳
    last_line = lines[-1].decode()
    last_timestamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', last_line).group(0)
    my_log.info(f"获取到首行时间戳：{first_timestamp}，获取到尾行时间戳：{last_timestamp}")
    return first_timestamp, last_timestamp


class CSVCaseManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.rows = []
        self.headers = []

    def read(self):
        """读取 CSV，返回字典列表"""
        with open(self.filepath, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.rows = [row for row in reader if any(row.values())]
            self.headers = reader.fieldnames
        return self.rows

    def write(self, rows):
        """写入多行字典（覆盖写）"""
        if not rows:
            raise ValueError("写入数据不能为空")
        self.headers = list(rows[0].keys())
        with open(self.filepath, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(rows)
        self.rows = rows

    def save(self):
        """保存当前内存中的 rows 到文件"""
        self.write(self.rows)

    def update_by_conditions(self, conditions: dict, updates: dict):
        """根据多条件匹配并更新所有符合条件的行，立即写入"""
        updated = False
        for row in self.rows:
            if all(row.get(k) == str(v) for k, v in conditions.items()):
                row.update(updates)
                updated = True
        if updated:
            self.save()
        return updated

    def get_row_by_conditions(self, conditions: dict):
        """返回唯一匹配条件的行引用（可修改）"""
        matches = [row for row in self.rows if all(row.get(k) == str(v) for k, v in conditions.items())]
        if len(matches) == 0:
            raise ValueError("❌ 没有匹配的行")
        elif len(matches) > 1:
            raise ValueError("⚠️ 匹配了多行，请确认条件是否足够唯一")
        return matches[0]

    def filter_and_save_as(self, new_filepath, condition_list):
        """
        根据多个字典条件筛选行（任意一个条件组匹配即可），另存为新文件
        :param new_filepath: 保存的新文件路径
        :param condition_list: 匹配条件列表，每个元素是字典（AND），字典间为 OR
        :return: 新的 CSVCaseManager 实例
        """
        if not self.rows:
            self.read()

        def matches_any(row):
            for cond in condition_list:
                if all(str(row.get(k)) == str(v) for k, v in cond.items()):
                    return True
            return False

        filtered = [row for row in self.rows if matches_any(row)]

        if not filtered:
            raise ValueError("❗未找到匹配条件的用例")

        new_mgr = CSVCaseManager(new_filepath)
        new_mgr.write(filtered)
        return new_mgr


if __name__ == '__main__':
    # excel_path = r'../data/common/case_/xmind_to_case.xlsx'
    # sheet_name = 'Sheet'
    # read_excel = ReadExcel(excel_path, sheet_name)
    # print(read_excel.keys)
    # print(read_excel.max_row)
    # print(read_excel.max_col)
    # print(read_excel.dict_data())
    # 调用函数进行测试
    # file_path = r"D:\WorkSpace\AGVHelper\小胖熊_中间_E35_直线15m_直线转弯5m_15°放托盘\托盘堆垛解垛.tkl"
    # number = 50  # 替换为你要复制的次数
    # copy_file_content(file_path, number)
    #
    csv_file = "/home/visionnav/VNSim/vnsimautotest/test_case/get_put_sim_case_temp.csv"
    # copy_csv_path = create_file_copy(csv_file, copy=True)
    csv_cm = CSVCaseManager(csv_file)
    csv_cm.read()
    fil_mgr = csv_cm.filter_and_save_as(
        '/home/visionnav/VNSim/vnsimautotest/test_case/get_put_sim_case_temp_1.csv',
        [
            {'测试车型': 'E35_fwd_3mid360_bw_2mid360', '任务流程列表': '伺服卷积托盘冒烟'},
            {'测试车型': 'P15_fwd_3mid360_bw_2mid360', '任务流程列表': '伺服固定放货法冒烟'},
        ])
    # row = csv_cm.get_row_by_conditions({'标题': '识别不到载具', '测试车型': 'P15_fwd_3mid360_bw_2mid360', '任务流程列表': '伺服卷积托盘冒烟'})
    # # row.update({"用例状态": '已通过'})
    # row['用例状态'] = '已通过'
    # csv_cm.save()
    # result = csv_cm.update_by_conditions(
    #     {'标题': '识别不到载具', '测试车型': 'P15_fwd_3mid360_bw_2mid360', '任务流程列表': '伺服卷积托盘冒烟'},
    #     {'用例状态': '已通过'}
    # )
    # print(result)
