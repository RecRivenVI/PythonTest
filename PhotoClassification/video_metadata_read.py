import os
import json
import subprocess

def extract_xiaomi_tags(file_path):
    """
    从单个文件提取以 com.xiaomi. 开头的字段。
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_format",
                "-of", "json",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 解析 JSON 数据
        data = json.loads(result.stdout)
        
        # 检查 format.tags 并提取 com.xiaomi. 前缀的字段
        if "format" in data and "tags" in data["format"]:
            tags = data["format"]["tags"]
            xiaomi_tags = {key: value for key, value in tags.items() if key.startswith("com.xiaomi.")}
            if xiaomi_tags:  # 如果有匹配的字段
                print(f"File: {file_path}")
                print(json.dumps(xiaomi_tags, indent=4))
        else:
            print(f"File: {file_path} - No Xiaomi tags found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for file {file_path}: {e}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def process_directory(directory):
    """
    遍历目录下的所有文件并提取 Xiaomi 的字段。
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            extract_xiaomi_tags(file_path)

# 示例目录路径
directory_path = r"F:\PhotoClassification\Me\slow_moment1"
process_directory(directory_path)
