import os
import pandas as pd
from datetime import datetime

# 定义要扫描的目录
directories = [
    (r'F:\PhotoClassification\Me\Categorized\Screenshots', '自己'),
    (r'F:\PhotoClassification\Mom\Categorized\Screenshots', '老妈')
]
csv_output_path = 'screenshots_info.csv'

# 初始化数据列表
data = []

# 遍历文件夹
for base_directory, user in directories:
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)

        # 检查是否是文件夹
        if os.path.isdir(folder_path):
            # 提取设备型号（第三段）
            parts = folder_name.split(' ')
            if len(parts) >= 3:
                device_model = ' '.join(parts[2:])

                # 遍历文件夹中的文件
                for file_name in os.listdir(folder_path):
                    if file_name.startswith('Screenshot_'):
                        # 提取时间信息
                        time_part = file_name[11:29]  # 从文件名中提取日期和时间部分
                        screenshot_time = datetime.strptime(time_part, '%Y-%m-%d-%H-%M-%S')

                        # 构建数据行
                        data.append({
                            '文件名称': file_name,
                            '截图时间': screenshot_time,
                            '设备型号': device_model,
                            '用户': user  # 添加用户信息
                        })

# 创建 DataFrame 并按照截图时间排序
df = pd.DataFrame(data)
df = df.sort_values(by='截图时间')  # 按截图时间排序

# 保存为 CSV 文件
df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')

print(f"CSV 文件已生成并按照截图时间排序：{csv_output_path}")
