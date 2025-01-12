import requests
import csv
import os

# 请求数据的 URL
url = "http://127.0.0.1:3000/get_friend_list"

# 输出的 CSV 文件名
output_file = "friend_list.csv"

try:
    # 发送 GET 请求
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    # 检查返回的数据状态
    if data.get("status") == "ok" and "data" in data:
        friend_data = data["data"]

        if not friend_data:
            print("返回的好友列表为空。")
            exit()

        # 按第一个对象的字段顺序提取字段名
        headers = list(friend_data[0].keys())

        # 写入 CSV 文件
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # 写入每条数据
            for friend in friend_data:
                writer.writerow({field: friend.get(field, "") for field in headers})

        print(f"好友列表已成功保存到 {os.path.abspath(output_file)}")
    else:
        print("获取的数据状态异常或数据字段缺失！")
except requests.RequestException as e:
    print(f"请求失败：{e}")
except Exception as e:
    print(f"处理数据时发生错误：{e}")
