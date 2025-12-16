import json
import csv
from datetime import datetime
import os

# --- 配置 ---
INPUT_FILE = 'index.json'           # 输入文件名
OUTPUT_FILE = 'minecraft_versions.csv'  # 输出文件名

def process_minecraft_data(input_path, output_path):
    # 1. 检查文件
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 '{input_path}'，请确认文件在当前目录下。")
        return

    # 2. 读取 JSON
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 JSON 失败: {e}")
        return

    # 3. 提取并筛选 "type": "release"
    versions_list = data.get('versions', [])
    releases = [v for v in versions_list if v.get('type') == 'release']

    if not releases:
        print("提示: JSON 中没有找到 'type': 'release' 的版本。")
        
    # 4. 排序
    # 注意：这里依然使用完整时间进行排序，以防止同一天发布多个版本时顺序错误
    releases.sort(key=lambda x: datetime.fromisoformat(x['releaseTime']))

    # 5. 处理数据 (生成新版本号 + 格式化日期)
    csv_rows = []
    year_counters = {}  # 计数器：{2024: 1, 2025: 2, ...}

    for item in releases:
        ver = item.get('version')
        raw_time = item.get('releaseTime')
        
        # 将字符串转为 datetime 对象
        dt = datetime.fromisoformat(raw_time)
        year = dt.year
        
        # --- 逻辑 A: 生成新版本号 (25.1, 25.2 ...) ---
        if year not in year_counters:
            year_counters[year] = 1
        else:
            year_counters[year] += 1
            
        short_year = str(year)[-2:] # 取年份后两位
        new_ver = f"{short_year}.{year_counters[year]}"
        
        # --- 逻辑 B: 格式化日期 (仅保留 YYYY-MM-DD) ---
        date_only = dt.strftime('%Y-%m-%d')
        
        # 添加到结果
        csv_rows.append({
            "version": ver,
            "releaseTime": date_only,  # 这里只输出日期
            "new version": new_ver
        })

    # 6. 写入 CSV
    try:
        headers = ["version", "releaseTime", "new version"]
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            
        print(f"处理完成！")
        print(f"已生成文件: {output_path}")
        print(f"包含版本数: {len(csv_rows)}")
        
    except IOError as e:
        print(f"写入 CSV 失败: {e}")

if __name__ == "__main__":
    process_minecraft_data(INPUT_FILE, OUTPUT_FILE)