import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from collections import defaultdict

# 获取图片的EXIF信息中的日期时间
def get_image_date_taken(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "DateTimeOriginal":
                return value
    return None

# 将日期时间转换为目标格式
def format_date_time(exif_date):
    date_time_obj = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
    return date_time_obj.strftime("IMG_%Y%m%d_%H%M%S")

# 将有相同拍摄时间的文件移动到一个文件夹
def group_images_by_date(directory, target_directory):
    # 存储具有相同日期的图片，使用字典，键为拍摄时间
    date_groups = defaultdict(list)

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(directory, filename)
            exif_date = get_image_date_taken(image_path)

            if exif_date:
                formatted_date = format_date_time(exif_date)
                date_groups[formatted_date].append(image_path)

    # 创建目标目录并移动文件
    for date, image_paths in date_groups.items():
        if len(image_paths) > 1:  # 仅处理有相同拍摄时间的组
            # 为这组图片创建一个子文件夹
            subfolder_path = os.path.join(target_directory, date)
            os.makedirs(subfolder_path, exist_ok=True)

            for idx, image_path in enumerate(image_paths):
                # 如果是第一张，保留原始命名，后续添加后缀 _1, _2...
                new_filename = os.path.basename(image_path)
                if idx > 0:
                    name, ext = os.path.splitext(new_filename)
                    new_filename = f"{name}_{idx}{ext}"
                
                # 移动文件
                new_path = os.path.join(subfolder_path, new_filename)
                shutil.move(image_path, new_path)
                print(f"Moved {image_path} to {new_path}")

# 指定照片的目录路径和目标目录
source_directory = r'D:\分类\Xiaomi'
target_directory = r'D:\分类\时间相同'

# 开始处理
group_images_by_date(source_directory, target_directory)
