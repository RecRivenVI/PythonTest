import os
import csv

# 读取CSV文件中的内容
def parse_csv_file(csv_file_path):
    rename_map = {}
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) < 2:  # 确保每行有足够的列
                continue
            code = row[0].strip()  # 第一列为设备代号
            model_name = row[1].strip()  # 第二列为设备型号
            # 去掉设备名称中的 "China"
            cleaned_model_name = model_name.replace('China', '').strip()
            rename_map[code] = cleaned_model_name
    return rename_map

# 遍历文件夹并重命名匹配到的文件夹
def rename_folders(base_folder, rename_map):
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            # 仅去掉文件夹名中的空格
            normalized_folder_name = folder_name.replace(' ', '')

            # 在 rename_map 中查找处理后的文件夹名
            matched_key = None
            for code in rename_map:
                normalized_code = code.replace(' ', '')
                # 打印调试信息以查看具体对比情况
                # print(f"Comparing: '{normalized_folder_name}' with '{normalized_code}'")
                
                if normalized_folder_name == normalized_code:
                    matched_key = code
                    break

            if matched_key:
                new_name = rename_map[matched_key]
                new_folder_path = os.path.join(base_folder, new_name)
                try:
                    os.rename(folder_path, new_folder_path)
                    print(f"Renamed: {folder_name} -> {new_name}")
                except FileExistsError:
                    print(f"Error: {new_folder_path} already exists.")
            else:
                print(f"Skipped: {folder_name}")

# 主程序
if __name__ == "__main__":
    csv_file_path = 'model.csv'  # 替换为实际的CSV文件路径
    base_folder = r'F:\PhotoClassification\Mom\Categorized\MiuiCamera'  # 替换为实际的文件夹路径

    # 解析CSV文件并生成重命名映射
    rename_map = parse_csv_file(csv_file_path)

    # 重命名文件夹
    rename_folders(base_folder, rename_map)
