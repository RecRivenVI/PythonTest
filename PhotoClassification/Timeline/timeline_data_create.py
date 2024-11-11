import os
import subprocess
from PIL import Image
from PIL.ExifTags import TAGS
import pandas as pd
from datetime import datetime, timedelta
import warnings
from concurrent.futures import ThreadPoolExecutor

# 提高解压缩图片像素限制，允许更大尺寸的图像
Image.MAX_IMAGE_PIXELS = None

# 读取文本文档中的文件夹路径
def load_folders_from_file(file_path):
    folders = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            folder_path = line.strip()  # 直接读取路径，不做额外处理
            if os.path.exists(folder_path):
                folders.append(folder_path)
    return folders

# 从文本文档中加载文件夹列表
folder_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline_folder_paths.txt')
folders = load_folders_from_file(folder_file_path)

# 定义拍摄信息列表
photo_data = []
video_data = []
corrupt_images = []  # 用于存储有损坏 EXIF 数据的照片

# 读取照片的拍摄时间
def get_photo_taken_time(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':  # 获取拍摄时间
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        else:
            print(f"无法读取照片 {image_path} 的 EXIF 数据，可能已损坏")
            corrupt_images.append(image_path)
    except Exception as e:
        print(f"无法读取照片 {image_path} 的拍摄时间: {e}")
        corrupt_images.append(image_path)
    return None

# 获取视频的创建时间
def get_video_taken_time(video_path):
    try:
        # 获取视频的创建时间
        cmd_creation_time = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'format_tags=creation_time',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        creation_time_output = subprocess.check_output(cmd_creation_time).decode().strip()

        if creation_time_output:
            # 解析 creation_time 为 datetime 对象
            creation_time = datetime.strptime(creation_time_output, '%Y-%m-%dT%H:%M:%S.%fZ')
            
            # 获取视频的时长
            cmd_duration = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            duration_output = subprocess.check_output(cmd_duration).decode().strip()
            duration = float(duration_output)  # 视频时长，单位为秒

            # 计算实际拍摄时间 = 创建时间 - 视频时长
            adjusted_time = creation_time - timedelta(seconds=duration)

            # 将时间从 UTC 转换为本地时间 (假设东八区)
            local_time = adjusted_time + timedelta(hours=8)
            return local_time
        else:
            print(f"视频 {video_path} 缺少 creation_time 信息")
    except Exception as e:
        print(f"无法读取视频 {video_path} 的拍摄时间: {e}")
    return None

# 扫描文件夹中的照片和视频
def scan_folder(folder):
    # 根据路径提取用户和设备信息
    if 'Me' in folder:
        user = '自己'
    elif 'Mom' in folder:
        user = '老妈'
    else:
        user = '未知'

    phone_model = folder.split(os.sep)[-2]  # 提取设备型号

    # 使用路径的最后一级文件夹名称精确判断文件类型
    last_folder_name = os.path.basename(folder)
    
    if last_folder_name == 'IMG':
        file_type = '照片'
    elif last_folder_name == 'MVIMG':
        file_type = '动态照片'
    elif last_folder_name == 'VID':
        file_type = '视频'
    else:
        file_type = '未知类型'  # 未知文件夹类型，可以添加处理逻辑

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        # 对于照片类型
        if file_type == '照片' and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            taken_time = get_photo_taken_time(file_path)
            if taken_time:
                photo_data.append({
                    '文件名称': filename,
                    '拍摄时间': taken_time,
                    '设备型号': phone_model,
                    '用户': user,
                    '文件类型': file_type  # 根据文件夹直接赋值
                })
                print(f"读取照片: {file_path}, 拍摄时间: {taken_time}")

        # 对于动态照片
        elif file_type == '动态照片' and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            taken_time = get_photo_taken_time(file_path)
            if taken_time:
                photo_data.append({
                    '文件名称': filename,
                    '拍摄时间': taken_time,
                    '设备型号': phone_model,
                    '用户': user,
                    '文件类型': file_type  # 动态照片类型
                })
                print(f"读取动态照片: {file_path}, 拍摄时间: {taken_time}")

        # 对于视频类型
        elif file_type == '视频' and filename.lower().endswith(('.mp4', '.mov', '.avi')):
            taken_time = get_video_taken_time(file_path)
            if taken_time:
                video_data.append({
                    '文件名称': filename,
                    '拍摄时间': taken_time,
                    '设备型号': phone_model,
                    '用户': user,
                    '文件类型': file_type  # 视频类型
                })
                print(f"读取视频: {file_path}, 拍摄时间: {taken_time}")

# 忽略损坏 EXIF 数据的警告
warnings.simplefilter('ignore', UserWarning)

# 使用多线程遍历所有路径
with ThreadPoolExecutor() as executor:
    executor.map(scan_folder, folders)

# 将数据存储到 Pandas DataFrame
df_photos = pd.DataFrame(photo_data)
df_videos = pd.DataFrame(video_data)

# 合并照片和视频数据
df = pd.concat([df_photos, df_videos], ignore_index=True)

# 按拍摄时间排序
df.sort_values(by='拍摄时间', inplace=True)

# 输出到 CSV 文件
df.to_csv('timeline_data.csv', index=False, encoding='utf-8-sig')

print("表格已生成并保存为 'timeline_data.csv'")

# 输出有损坏 EXIF 数据的照片列表
if corrupt_images:
    print("\n以下照片的 EXIF 数据损坏或无法读取：")
    for img in corrupt_images:
        print(img)
