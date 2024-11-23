import os
import json
import hashlib
import subprocess
from datetime import datetime, timedelta

def extract_xiaomi_tags(file_path):
    """
    从文件提取以 com.xiaomi. 开头的字段。
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
        if "format" in data and "tags" in data["format"]:
            tags = data["format"]["tags"]
            xiaomi_tags = {key: value for key, value in tags.items() if key.startswith("com.xiaomi.")}
            return xiaomi_tags
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return {}

def get_video_frame_rate(file_path):
    """
    获取视频的帧速率，优先使用 avg_frame_rate。
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",  # 选择视频流
                "-show_entries", "stream=avg_frame_rate,r_frame_rate,tbr,tbn",  # 获取 avg_frame_rate, r_frame_rate, tbr, tbn
                "-of", "json",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        data = json.loads(result.stdout)
        
        if "streams" in data and len(data["streams"]) > 0:
            stream = data["streams"][0]
            avg_frame_rate = stream.get("avg_frame_rate")
            r_frame_rate = stream.get("r_frame_rate")
            
            if avg_frame_rate:
                num, den = map(int, avg_frame_rate.split("/"))
                frame_rate = num / den
                return frame_rate
            elif r_frame_rate:
                num, den = map(int, r_frame_rate.split("/"))
                frame_rate = num / den
                return frame_rate
            else:
                print(f"Warning: No frame rate found for file {file_path}")
        return 0
    except Exception as e:
        return 0

def get_video_taken_time(video_path):
    """
    提取视频拍摄时间，按拍摄时间生成文件名基础部分。
    """
    try:
        cmd_creation_time = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'format_tags=creation_time',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        creation_time_output = subprocess.check_output(cmd_creation_time).decode().strip()
        if creation_time_output:
            creation_time = datetime.strptime(creation_time_output, '%Y-%m-%dT%H:%M:%S.%fZ')
            cmd_duration = [
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            duration_output = subprocess.check_output(cmd_duration).decode().strip()
            duration = float(duration_output)
            adjusted_time = creation_time - timedelta(seconds=duration)
            local_time = adjusted_time + timedelta(hours=8)
            return local_time
    except Exception:
        pass
    return None

def calculate_file_hash(file_path, block_size=65536):
    """
    计算文件的 MD5 哈希值。
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(block_size)
    return hasher.hexdigest()

def get_unique_filename(directory, base_name, ext, original_file_hash):
    """
    确保文件名唯一，避免文件名冲突。
    """
    new_name = base_name + ext
    counter = 1
    while os.path.exists(os.path.join(directory, new_name)):
        existing_file_path = os.path.join(directory, new_name)
        existing_file_hash = calculate_file_hash(existing_file_path)
        if existing_file_hash == original_file_hash:
            return new_name
        else:
            new_name = f"{base_name}_{counter}{ext}"
            counter += 1
    return new_name

def round_to_nearest_10(value):
    """
    将一个值四舍五入到最接近的10的整数倍
    """
    return round(value / 10) * 10

def is_frame_rate_matching(slow_moment_value, actual_frame_rate):
    """
    判断视频的实际帧速率是否与 com.xiaomi.slow_moment 的值匹配。
    将实际帧速率四舍五入为最接近的 10 的整数倍后再进行比较。
    """
    try:
        # 将 slow_moment_value 转换为整数
        slow_moment_value = int(float(slow_moment_value))  # 转换为整数
        # 将实际帧率四舍五入为最接近的 10 的整数倍
        actual_frame_rate = round_to_nearest_10(float(actual_frame_rate))  # 四舍五入为 10 的倍数
        
        return actual_frame_rate == slow_moment_value
    except ValueError:
        return False

def rename_videos_in_directory(directory):
    """
    遍历目录中的所有视频文件并进行重命名，同时输出调试信息。
    """
    log_file = os.path.join(os.path.dirname(__file__), "video_rename_log.txt")  # 日志文件路径
    with open(log_file, "a") as log:  # 以附加模式打开日志文件
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in ('.mp4', '.mov', '.avi', '.mkv'):
                    video_date = get_video_taken_time(file_path)
                    xiaomi_tags = extract_xiaomi_tags(file_path)
                    if video_date:
                        formatted_date = video_date.strftime("VID_%Y%m%d_%H%M%S")
                        
                        # 检测 Xiaomi 特定字段并添加后缀
                        suffix = ""
                        if "com.xiaomi.hdr10" in xiaomi_tags and xiaomi_tags["com.xiaomi.hdr10"] == "28516":
                            suffix += "_DOLBY"
                        
                        # 处理 slow_moment 字段
                        if "com.xiaomi.slow_moment" in xiaomi_tags:
                            slow_value = xiaomi_tags["com.xiaomi.slow_moment"]
                            actual_frame_rate = get_video_frame_rate(file_path)
                            
                            # 比较 slow_moment 和帧速率
                            if slow_value.isdigit():
                                if is_frame_rate_matching(slow_value, actual_frame_rate):
                                    suffix += f"_HSR_{slow_value}"
                            
                        # 获取文件哈希值并生成新的文件名
                        file_hash = calculate_file_hash(file_path)
                        new_name = get_unique_filename(root, formatted_date + suffix, file_ext, file_hash)
                        new_path = os.path.join(root, new_name)
                        
                        # 写入日志并重命名文件
                        if new_name != filename:
                            os.rename(file_path, new_path)
                    #        log.write(f"  [INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Renamed\n")
                            log.write(f"    Original: {filename}\n")
                            log.write(f"    Renamed:  {new_name}\n\n")  # 格式化输出日志
                            print(f"Renamed {filename} to {new_name}")
                    #    else:
                    #        log.write(f"  [INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Skipped\n")
                    #        log.write(f"    Original: {filename}\n")
                    #        log.write(f"    Reason: Name unchanged\n\n")
                    else:
                        log.write(f"  [INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No creation time\n")
                        log.write(f"    File: {filename}\n")
                        log.write(f"    Reason: No creation time found\n\n")
                        print(f"No creation time found for video {filename}")

# 示例目录路径
directory_path = r"F:\PhotoClassification\Me\Uncategorized\Videos"
rename_videos_in_directory(directory_path)
