import csv
import os

# 文件名定义
duplicated_users_file = "duplicated_users.csv"
friend_list_file = "friend_list.csv"
output_file = "duplicated_users_friend.csv"

# 仅保留的 group_id 列表
FILTERED_GROUP_IDS = {
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

    # 读取 duplicated_users.csv 并筛选指定 group_id 的记录
    filtered_rows = []
    user_ids_in_marked_groups = set()  # 存储在 MARKED_GROUP_IDS 中的 user_id

    with open(duplicated_users_file, mode="r", encoding="gbk", errors="ignore") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ["friend", "is_marked"]  # 在原字段基础上添加 friend 和 is_marked 字段

        if MARKED_GROUP_IDS:  # 检查 MARKED_GROUP_IDS 是否为空
            # 首先遍历数据，标记所有需要标记为 marked 的 user_id
            for row in reader:
                user_id = row["user_id"]
                group_id = row["group_id"]

                # 如果 group_id 在 MARKED_GROUP_IDS 中，则将该用户标记为 marked
                if group_id in MARKED_GROUP_IDS:
                    user_ids_in_marked_groups.add(user_id)

            file.seek(0)  # 重新定位到文件开头
            next(reader)  # 跳过表头

        for row in reader:
            user_id = row["user_id"]
            group_id = row["group_id"]

            # 检查 FILTERED_GROUP_IDS 是否为空
            if not FILTERED_GROUP_IDS or group_id in FILTERED_GROUP_IDS:
                # 为需要标记为 marked 的用户添加 is_marked 字段
                row["is_marked"] = "TRUE" if user_id in user_ids_in_marked_groups else "FALSE"
                
                # 添加 friend 字段
                row["friend"] = "TRUE" if user_id in friend_user_ids else "FALSE"
                filtered_rows.append(row)

    # 将筛选结果写入新的 CSV 文件
    with open(output_file, mode="w", encoding="gbk", newline="", errors="ignore") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

    print(f"处理完成，结果已保存到 {os.path.abspath(output_file)}")
except Exception as e:
    print(f"处理数据时发生错误：{e}")
