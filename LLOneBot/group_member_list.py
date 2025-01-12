import requests
import csv
import os

# 请求数据的 URL
group_id = 744304553
url = f"http://127.0.0.1:3000/get_group_member_list?group_id={group_id}"

# 输出的 CSV 文件名
output_file = f"group_{group_id}_member_list.csv"

try:
    # 发送 GET 请求
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # 检查返回的数据状态
    if data.get("status") == "ok" and "data" in data:
        member_data = data["data"]

        # 指定 CSV 列名
        headers = [
            "group_id",
            "user_id",
            "nickname",
            "card",
            "sex",
            "age",
            "area",
            "level",
            "qq_level",
            "join_time",
            "last_sent_time",
            "title_expire_time",
            "unfriendly",
            "card_changeable",
            "is_robot",
            "shut_up_timestamp",
            "role",
            "title",
        ]

        # 写入 CSV 文件
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(member_data)

        print(f"群成员数据已成功保存到 {os.path.abspath(output_file)}")
    else:
        print("获取的数据状态异常或数据字段缺失！")
except requests.RequestException as e:
    print(f"请求失败：{e}")
except Exception as e:
    print(f"处理数据时发生错误：{e}")
