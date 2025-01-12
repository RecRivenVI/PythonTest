import os
import csv
from collections import defaultdict

OUTPUT_DIR = "group_members"
RESULT_FILE = "duplicated_users.csv"

def find_duplicated_users():
    user_data = defaultdict(list)  # 记录每个 user_id 的出现信息

    # 遍历输出目录下的所有 CSV 文件
    for file_name in os.listdir(OUTPUT_DIR):
        if file_name.endswith(".csv"):
            file_path = os.path.join(OUTPUT_DIR, file_name)
            with open(file_path, mode="r", encoding="gbk", errors="replace") as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames  # 动态获取字段名
                for row in reader:
                    user_id = row.get("user_id", "")  # 确保 user_id 存在
                    group_id = row.get("group_id", "")  # 确保 group_id 存在
                    group_name = row.get("group_name", "Unknown")  # 默认值为 "Unknown"
                    
                    # 记录该 user_id 的群信息
                    user_data[user_id].append({
                        **{field: row.get(field, "") for field in fieldnames},  # 按顺序补全字段
                        "group_name": group_name,  # 保留可能的缺失字段
                    })

    # 筛选重复的 user_id
    duplicated_users = {user_id: groups for user_id, groups in user_data.items() if len(groups) > 1}

    # 如果没有重复数据
    if not duplicated_users:
        print("没有找到重复的 user_id。")
        return

    # 输出结果到新的 CSV 文件
    with open(RESULT_FILE, mode="w", encoding="gbk", errors="replace", newline="") as csvfile:
        # 动态获取字段名并写入 CSV
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user_id, groups in duplicated_users.items():
            for group_info in groups:
                writer.writerow({field: group_info.get(field, "") for field in fieldnames})

    # 输出统计信息
    print(f"重复的用户信息已保存到 {RESULT_FILE}")
    print(f"找到 {len(duplicated_users)} 个重复用户，涉及 {sum(len(groups) for groups in duplicated_users.values())} 条记录。")

if __name__ == "__main__":
    find_duplicated_users()
