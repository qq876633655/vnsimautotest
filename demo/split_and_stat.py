import csv
import numpy as np

# 读取原始CSV文件
input_file = '/home/visionnav/VNSim/luoguancong/vnsimautotest/data_2025-04-17-16-42-57.csv'
point_num = 2
base_name, extension = input_file.rsplit('.', 1)
output_files = []

for i in range(point_num):
    new_input_file = f"{base_name}_part{i+1}.{extension}"
    output_files.append(new_input_file)

print(output_files)

# 初始化文件写入对象
writers = [open(file, 'w', newline='') for file in output_files]
csv_writers = [csv.writer(writer) for writer in writers]

# 读取并写入数据到不同的文件
with open(input_file, 'r') as infile:
    reader = csv.reader(infile)
    for i, row in enumerate(reader):
        csv_writers[i % point_num].writerow(row)

# 关闭文件写入对象
for writer in writers:
    writer.close()