import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

# 提高解压缩图片像素限制，允许更大尺寸的图像
Image.MAX_IMAGE_PIXELS = None

def is_mv_photo(file_path):
    """Check if the photo is a Micro Video (MVIMG)."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')  # 需要计算结束标签的长度
            if start == -1 or end == -1:
                return False
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xmp_string)
                ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
                      'GCamera': 'http://ns.google.com/photos/1.0/camera/'}
                description = root.find('.//rdf:Description', ns)
                if description is not None:
                    micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                    return micro_video == "1"
            except ET.ParseError:
                return False
    except Exception:
        return False

def get_image_date_taken(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                if TAGS.get(tag, tag) == "DateTimeOriginal":
                    return value
    except Exception:
        pass
    return None

def calculate_file_hash(file_path, block_size=65536):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read(block_size)
        while len(buf) > 0:
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
        else:
            new_name = f"{base_name}_{counter}{ext}"
            counter += 1
    return new_name

def rename_images_in_directory(directory):
    log_file = os.path.join(os.path.dirname(__file__), "photo_rename_log.txt")  # 日志文件路径
    with open(log_file, "a") as log:  # 以附加模式打开日志文件
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in ('.jpg', '.jpeg', '.png'):
                    exif_date = get_image_date_taken(file_path)
                    if exif_date:
                        prefix = "MVIMG" if is_mv_photo(file_path) else "IMG"
                        try:
                            formatted_date = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S").strftime(f"{prefix}_%Y%m%d_%H%M%S")
                            file_hash = calculate_file_hash(file_path)
                            new_name = get_unique_filename(root, formatted_date, file_ext, file_hash)
                            new_path = os.path.join(root, new_name)
                            if new_name != filename:
                                os.rename(file_path, new_path)
                        #        log.write(f"  [INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Renamed\n")
                                log.write(f"    Original: {filename}\n")
                                log.write(f"    Renamed:  {new_name}\n\n")  # 格式化输出日志
                                print(f"Renamed {filename} to {new_name}")
                            #else:
                            #    print(f"Skipped renaming {filename}, as the name is unchanged.")
                        except ValueError:
                            print(f"Invalid EXIF date format for {filename}")
                    else:
                        print(f"No EXIF date found for {filename}")

directory_path = r"F:\PhotoClassification\Me\Uncategorized\photox"
rename_images_in_directory(directory_path)
