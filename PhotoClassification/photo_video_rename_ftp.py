import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
import subprocess
import xml.etree.ElementTree as ET
from ftplib import FTP
import tempfile
import shutil

# 提高解压缩图片像素限制，允许更大尺寸的图像
Image.MAX_IMAGE_PIXELS = None

# FTP 服务器信息
FTP_HOST = "192.168.0.92"
FTP_PORT = 2121
FTP_USER = ""
FTP_PASS = ""

# 检查照片是否是 MVIMG
def is_mv_photo(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
            if start == -1 or end == -1:
                return False
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')
            try:
                root = ET.fromstring(xmp_string)
            except ET.ParseError as e:
                print(f"XML parsing error in file {file_path}: {e}")
                return False
            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'GCamera': 'http://ns.google.com/photos/1.0/camera/'
            }
            description = root.find('.//rdf:Description', ns)
            if description is not None:
                micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                return micro_video == "1"
            return False
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
                if TAGS.get(tag, tag) == "DateTimeOriginal":
                    return value
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
    return None

# 获取视频的创建时间
def get_video_taken_time(video_path):
    try:
        cmd_creation_time = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'format_tags=creation_time', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        creation_time_output = subprocess.check_output(cmd_creation_time).decode().strip()
        if creation_time_output:
            creation_time = datetime.strptime(creation_time_output, '%Y-%m-%dT%H:%M:%S.%fZ')
            cmd_duration = [
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ]
            duration_output = subprocess.check_output(cmd_duration).decode().strip()
            duration = float(duration_output)
            local_time = creation_time - timedelta(seconds=duration) + timedelta(hours=8)
            return local_time
    except Exception as e:
        print(f"无法读取视频 {video_path} 的拍摄时间: {e}")
    return None

# 文件重命名逻辑
def format_date_time(date_time, prefix):
    try:
        return date_time.strftime(f"{prefix}_%Y%m%d_%H%M%S")
    except Exception as e:
        print(f"Error formatting date: {e}")
        return None

def calculate_file_hash(file_path, block_size=65536):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read(block_size)
        while buf:
            hasher.update(buf)
            buf = file.read(block_size)
    return hasher.hexdigest()

def get_unique_filename(directory, base_name, ext, original_file_hash):
    new_name = base_name + ext
    counter = 1
    while os.path.exists(os.path.join(directory, new_name)):
        existing_file_path = os.path.join(directory, new_name)
        existing_file_hash = calculate_file_hash(existing_file_path)
        if existing_file_hash == original_file_hash:
            return new_name
        new_name = f"{base_name}_{counter}{ext}"
        counter += 1
    return new_name

# 下载并重命名文件
def download_and_rename_files(ftp, remote_dir, local_dir):
    ftp.cwd(remote_dir)
    files = ftp.nlst()

    for filename in files:
        local_file_path = os.path.join(local_dir, filename)
        
        # 下载文件
        with open(local_file_path, 'wb') as f:
            ftp.retrbinary(f"RETR {filename}", f.write)
        
        ext = os.path.splitext(filename)[1].lower()
        new_name = filename
        
        # 判断文件类型并进行重命名
        if ext in ('.jpg', '.jpeg', '.png'):
            exif_date = get_image_date_taken(local_file_path)
            if exif_date:
                prefix = "MVIMG" if is_mv_photo(local_file_path) else "IMG"
                formatted_date = format_date_time(datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S"), prefix)
                if formatted_date:
                    file_hash = calculate_file_hash(local_file_path)
                    new_name = get_unique_filename(local_dir, formatted_date, ext, file_hash)
        elif ext in ('.mp4', '.mov', '.avi', '.mkv'):
            video_date = get_video_taken_time(local_file_path)
            if video_date:
                formatted_date = format_date_time(video_date, "VID")
                if formatted_date:
                    file_hash = calculate_file_hash(local_file_path)
                    new_name = get_unique_filename(local_dir, formatted_date, ext, file_hash)

        # 重命名本地文件
        new_local_file_path = os.path.join(local_dir, new_name)
        os.rename(local_file_path, new_local_file_path)
        
        # 上传重命名后的文件到 FTP 服务器
        with open(new_local_file_path, 'rb') as f:
            ftp.storbinary(f'STOR {new_name}', f)
        print(f"Renamed and uploaded {filename} to {new_name}")

        # 删除本地重命名后的文件
        os.remove(new_local_file_path)


# 主函数
def main():
    with FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            download_and_rename_files(ftp, "/Download/photo", temp_dir)

if __name__ == "__main__":
    main()
