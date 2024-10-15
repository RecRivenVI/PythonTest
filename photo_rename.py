import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

# 获取图片的EXIF信息中的日期时间
def get_image_date_taken(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return value
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
    
    return None

# 将日期时间转换为目标格式
def format_date_time(exif_date):
    try:
        date_time_obj = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
        return date_time_obj.strftime("IMG_%Y%m%d_%H%M%S")
    except Exception as e:
        print(f"Error formatting date: {e}")
        return None

# 计算文件的哈希值以判断内容是否相同
def calculate_file_hash(file_path, block_size=65536):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(block_size)
    return hasher.hexdigest()

# 确保新的文件名不会冲突，只有在文件内容不同的情况下才添加后缀
def get_unique_filename(directory, base_name, ext, original_file_hash):
    new_name = base_name + ext
    counter = 1
    while os.path.exists(os.path.join(directory, new_name)):
        existing_file_path = os.path.join(directory, new_name)
        existing_file_hash = calculate_file_hash(existing_file_path)
        
        if existing_file_hash == original_file_hash:
            # 文件内容相同，不需要重命名
            return new_name
        else:
            # 文件内容不同，添加后缀
            new_name = f"{base_name}_{counter}{ext}"
            counter += 1
    return new_name

# 遍历目录及其所有子目录中的图片并重命名
def rename_images_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(root, filename)
                exif_date = get_image_date_taken(image_path)
                
                if exif_date:
                    formatted_date = format_date_time(exif_date)
                    if formatted_date:
                        # 计算原始文件的哈希值
                        file_hash = calculate_file_hash(image_path)
                        
                        # 获取唯一文件名
                        new_name = get_unique_filename(root, formatted_date, os.path.splitext(filename)[1], file_hash)
                        new_path = os.path.join(root, new_name)
                        
                        try:
                            if new_name != filename:  # 仅在新名称和原名称不同时进行重命名
                                os.rename(image_path, new_path)
                                print(f"Renamed {filename} to {new_name}")
                            else:
                                print(f"Skipped renaming {filename}, as the name is unchanged.")
                        except Exception as e:
                            print(f"Error renaming {filename}: {e}")
                    else:
                        print(f"Invalid EXIF date format for {filename}")
                else:
                    print(f"No EXIF date found for {filename}")

# 指定照片的目录路径
directory_path = r"F:\照片整理目录\自己照片\分类\系统相机"
rename_images_in_directory(directory_path)
