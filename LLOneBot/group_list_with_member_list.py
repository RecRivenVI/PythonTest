import requests
import csv
import os

# 基础 URL
base_url = "http://127.0.0.1:3000"

# 输出目录
output_dir = "group_members"

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

def get_group_list():
    """获取群列表"""
    url = f"{base_url}/get_group_list"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok" and "data" in data:
            return data["data"]
        else:
            print("获取群列表失败：状态异常或数据字段缺失！")
    except requests.RequestException as e:
        print(f"请求群列表失败：{e}")
    return []

def get_group_member_list(group_id):
    """获取指定群的成员列表"""
    url = f"{base_url}/get_group_member_list?group_id={group_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok" and "data" in data:
            return data["data"]
        else:
            print(f"获取群 {group_id} 成员列表失败：状态异常或数据字段缺失！")
    except requests.RequestException as e:
        print(f"请求群 {group_id} 成员列表失败：{e}")
    return []

def save_to_csv(group_info, member_data):
    """将群信息和成员数据保存到 CSV 文件 (GBK 编码，跳过非法字符)"""
    group_id = group_info["group_id"]
    output_file = os.path.join(output_dir, f"group_{group_id}_member_list.csv")

    # 获取动态字段名
    group_fields = list(group_info.keys())
    member_fields = list(member_data[0].keys()) if member_data else []
    headers = group_fields + member_fields  # 合并字段名，群字段在前

    # 为每个成员添加群信息
    for member in member_data:
        member.update(group_info)

    try:
        # 用 GBK 编码保存，跳过非法字符
        with open(output_file, mode="w", newline="", encoding="gbk", errors="replace") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(member_data)
        print(f"群 {group_id} 的成员数据已保存到 {output_file}")
    except Exception as e:
        print(f"保存群 {group_id} 数据时出错：{e}")

def safe_print(*args, **kwargs):
    """安全打印，替换非法字符"""
    text = " ".join(str(arg) for arg in args)
    try:
        print(text.encode("gbk", errors="replace").decode("gbk"), **kwargs)
    except Exception as e:
        print(f"[打印错误] {e}")

def main():
    # 第一步：获取群列表
    group_list = get_group_list()
    if not group_list:
        safe_print("未能获取到任何群数据，程序终止。")
        return

    # 第二步：查询每个群的成员列表
    for group in group_list:
        group_id = group["group_id"]
        safe_print(f"正在获取群 {group_id} ({group['group_name']}) 的成员列表...")
        member_data = get_group_member_list(group_id)
        if member_data:
            save_to_csv(group, member_data)

if __name__ == "__main__":
    main()
