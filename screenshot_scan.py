import os
import csv

# 文件夹路径
folder_path = r'F:\PhotoClassification\Me\Categorized\Screenshots'
# 输出 CSV 文件名
output_csv = 'screenshot_packages.csv'

# 扫描文件夹并提取包名
packages = set()  # 使用集合防止包名重复
for filename in os.listdir(folder_path):
    # 只处理以 "Screenshot_" 开头的文件，忽略扩展名类型
    if filename.startswith('Screenshot_'):
        # 移除扩展名，分割文件名
        file_without_extension = os.path.splitext(filename)[0]
        parts = file_without_extension.split('_', 2)  # 只分割两次，获取第三部分
        if len(parts) == 3:
            package_name = parts[2]  # 提取第二部分后面的内容
            packages.add(package_name)

# 将包名列表按字母顺序排序
sorted_packages = sorted(packages)

# 将结果写入 CSV 文件
with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Package Name'])  # 写入表头
    for package in sorted_packages:
        writer.writerow([package])

print(f"CSV 文件已生成，保存在: {output_csv}")
