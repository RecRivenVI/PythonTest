import csv
import re

# 输入和输出文件路径
md_file_path = 'model.md'  # 替换为你的md文件路径
csv_file_path = 'model.csv'  # 输出的CSV文件路径

# 读取md文件并提取信息
device_data = []
with open(md_file_path, 'r', encoding='utf-8') as md_file:
    for line in md_file:
        # 跳过空行
        if not line.strip():
            continue
        # 使用正则表达式提取设备代号和设备型号
        match = re.match(r'`([^`]+?)`: (.+)', line.strip())
        if match:
            device_codes = [code.strip() for code in match.group(1).split('`') if code.strip()]  # 按反引号分割并去除空格
            device_model = match.group(2)
            for device_code in device_codes:
                device_data.append([device_code, device_model])  # 添加到列表

# 将提取的信息写入CSV文件
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Device Code', 'Device Model'])  # 写入表头
    writer.writerows(device_data)  # 写入设备数据

print(f'已成功将数据转换为 {csv_file_path}')