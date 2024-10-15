import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
import subprocess
import xml.etree.ElementTree as ET

# 检查照片是否是 MVIMG
def is_mv_photo(file_path):
    """Check if the photo is a Micro Video (MVIMG)."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

            # Find XMP data within the file
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
            
            if start == -1 or end == -1:
                return False  # No XMP data found
            
            # Extract XMP data and decode it to a string
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')

            # Parse XML from the XMP data
            try:
                root = ET.fromstring(xmp_string)
            except ET.ParseError as e:
                print(f"XML parsing error in file {file_path}: {e}")
                return False

            # Define the namespaces for parsing
            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'x': 'adobe:ns:meta/',
                'GCamera': 'http://ns.google.com/photos/1.0/camera/',
                'MiCamera': 'http://ns.xiaomi.com/photos/1.0/camera/'
            }

            # Find the rdf:Description element
            description = root.find('.//rdf:Description', ns)

            if description is not None:
                # Check if the MicroVideo attribute exists and its value is "1"
                micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                
                if micro_video == "1":
                    return True  # This is a Micro Video (MVIMG)

            return False  # Not an MVIMG

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

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

# 获取视频的创建时间
def get_video_taken_time(video_path):
    try:
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

# 将日期时间转换为目标格式
def format_date_time(date_time, prefix):
    try:
        return date_time.strftime(f"{prefix}_%Y%m%d_%H%M%S")
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

# 遍历目录及其所有子目录中的图片和视频并重命名
def rename_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext in ('.jpg', '.jpeg', '.png'):
                # 处理图片
                exif_date = get_image_date_taken(file_path)
                
                if exif_date:
                    # 判断是否是 MVIMG
                    prefix = "MVIMG" if is_mv_photo(file_path) else "IMG"
                    formatted_date = format_date_time(datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S"), prefix)
                    if formatted_date:
                        # 计算原始文件的哈希值
                        file_hash = calculate_file_hash(file_path)
                        
                        # 获取唯一文件名
                        new_name = get_unique_filename(root, formatted_date, file_ext, file_hash)
                        new_path = os.path.join(root, new_name)
                        
                        try:
                            if new_name != filename:  # 仅在新名称和原名称不同时进行重命名
                                os.rename(file_path, new_path)
                                print(f"Renamed {filename} to {new_name}")
                            else:
                                print(f"Skipped renaming {filename}, as the name is unchanged.")
                        except Exception as e:
                            print(f"Error renaming {filename}: {e}")
                    else:
                        print(f"Invalid EXIF date format for {filename}")
                else:
                    print(f"No EXIF date found for {filename}")

            elif file_ext in ('.mp4', '.mov', '.avi', '.mkv'):
                # 处理视频
                video_date = get_video_taken_time(file_path)
                
                if video_date:
                    formatted_date = format_date_time(video_date, "VID")
                    if formatted_date:
                        # 计算原始文件的哈希值
                        file_hash = calculate_file_hash(file_path)
                        
                        # 获取唯一文件名
                        new_name = get_unique_filename(root, formatted_date, file_ext, file_hash)
                        new_path = os.path.join(root, new_name)
                        
                        try:
                            if new_name != filename:  # 仅在新名称和原名称不同时进行重命名
                                os.rename(file_path, new_path)
                                print(f"Renamed {filename} to {new_name}")
                            else:
                                print(f"Skipped renaming {filename}, as the name is unchanged.")
                        except Exception as e:
                            print(f"Error renaming {filename}: {e}")
                    else:
                        print(f"Invalid video date format for {filename}")
                else:
                    print(f"No creation time found for video {filename}")

# 指定文件的目录路径
directory_path = r"F:\PhotoClassification\test"
rename_files_in_directory(directory_path)
