import csv
import os
from collections import Counter

# 文件名定义
duplicated_users_file = "duplicated_users.csv"
friend_list_file = "friend_list.csv"
output_file = "duplicated_users_friend_GLT.csv"

# 仅保留的 group_id 列表
FILTERED_GROUP_IDS = {
    "683885461", "676092890", "549469813", "945477199", 
    "415948551", "535949049", "113893015", "161362456", 
    "457057264", "829010981", "885435615", "649039513", 
    "681691883", "553098907", "982655391", "750903149", 
    "934319295", "174113785", "994103958", "935065119"
}

# 需要标记为 marked 的 group_id 列表
MARKED_GROUP_IDS = {
}

try:
    # 读取 friend_list 中的 user_id
    friend_user_ids = set()
    with open(friend_list_file, mode="r", encoding="gbk", errors="ignore") as file:
        reader = csv.DictReader(file)
        for row in reader:
            friend_user_ids.add(row["user_id"])  # 将所有 user_id 加入集合

    # 读取 duplicated_users.csv，标记所有需要的 user_id
    user_ids_in_marked_groups = set()  # 用于存储所有需要标记为 marked 的 user_id
    user_group_counter = Counter()  # 用于统计 user_id 在 FILTERED_GROUP_IDS 中的出现次数

    with open(duplicated_users_file, mode="r", encoding="gbk", errors="ignore") as file:
        reader = csv.DictReader(file)

        # 首次遍历，记录所有需要标记为 marked 的 user_id
        for row in reader:
            user_id = row["user_id"]
            group_id = row["group_id"]

            # 如果 group_id 在 MARKED_GROUP_IDS 中，则将该用户标记为 marked
            if group_id in MARKED_GROUP_IDS:
                user_ids_in_marked_groups.add(user_id)

            # 如果 group_id 在 FILTERED_GROUP_IDS 中，统计其出现次数
            if group_id in FILTERED_GROUP_IDS:
                user_group_counter[user_id] += 1

        file.seek(0)  # 重新定位到文件开头
        next(reader)  # 跳过表头

        # 过滤数据并添加标记
        filtered_rows = []
        fieldnames = reader.fieldnames + ["friend", "is_marked"]  # 原字段基础上添加 friend 和 is_marked 字段

        for row in reader:
            user_id = row["user_id"]
            group_id = row["group_id"]

            # 检查 FILTERED_GROUP_IDS 是否为空
            if not FILTERED_GROUP_IDS or group_id in FILTERED_GROUP_IDS:
                # 添加 is_marked 字段（根据用户是否在标记组中）
                row["is_marked"] = "TRUE" if user_id in user_ids_in_marked_groups else "FALSE"
                
                # 添加 friend 字段
                row["friend"] = "TRUE" if user_id in friend_user_ids else "FALSE"
                filtered_rows.append(row)

    # 确保最终结果中只保留在 FILTERED_GROUP_IDS 内出现多次的 user_id
    final_rows = [row for row in filtered_rows if user_group_counter[row["user_id"]] > 1]

    # 将筛选结果写入新的 CSV 文件
    with open(output_file, mode="w", encoding="gbk", newline="", errors="ignore") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"处理完成，结果已保存到 {os.path.abspath(output_file)}")
except Exception as e:
    print(f"处理数据时发生错误：{e}")
