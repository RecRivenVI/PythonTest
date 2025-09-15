import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import subprocess
import xml.etree.ElementTree as ET
import sys

# 设置标准输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 提高解压缩图片像素限制，允许更大尺寸的图像
Image.MAX_IMAGE_PIXELS = None

def get_exif_data(image_path):
    """从图像中提取EXIF数据。"""
    image = Image.open(image_path)
    exif_data = image._getexif()  # 获取图像的EXIF数据
    exif = {}

    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif[tag_name] = value
    return exif

def get_video_metadata_ffprobe(video_path):
    """使用ffprobe提取视频元数据。"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'default=noprint_wrappers=1', video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    metadata = result.stdout
    return metadata

def extract_metadata_field(metadata, field_name):
    """从元数据中提取特定字段。"""
    match = re.search(f'{field_name}=(.*)', metadata)
    if match:
        return match.group(1).strip()
    return None

def is_mv_photo(file_path):
    """检查照片是否为微视频（MVIMG）。"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

            # 查找XMP数据
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
            
            if start == -1 or end == -1:
                return False
            
            # 提取XMP数据并解码
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')

            # 解析XML
            root = ET.fromstring(xmp_string)

            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'x': 'adobe:ns:meta/',
                'GCamera': 'http://ns.google.com/photos/1.0/camera/',
                'MiCamera': 'http://ns.xiaomi.com/photos/1.0/camera/'
            }

            description = root.find('.//rdf:Description', ns)

            # 检查是否找到rdf:Description
            if description is not None:
                micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                
                if micro_video == "1":
                    return True

            return False

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def sanitize_folder_name(name):
    """清理文件夹名称，移除首尾空格和null字符。"""
    if name is None:
        return ''
    return re.sub(r'\0', ' ', name).strip()  # 移除null字符并修剪空格

def organize_files_by_device(source_dir, destination_dir):
    """根据制造商和型号组织图片和视频文件。"""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        print(f'正在处理目录: {root}')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]

            # 初始化文件夹创建标志
            has_img = False
            has_mvimg = False
            has_vid = False

            # 处理图片
            if ext in ('jpg', 'jpeg', 'png', 'tiff', 'bmp'):
                try:
                    exif = get_exif_data(file_path)
                    manufacturer = sanitize_folder_name(exif.get('Make'))
                    camera_model = sanitize_folder_name(exif.get('Model'))

                    # 仅在找到制造商和型号时继续处理
                    if manufacturer and camera_model:
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, camera_model)

                        # 检查是否需要创建MVIMG或IMG文件夹
                        img_folder = os.path.join(model_folder, 'IMG')
                        mvimg_folder = os.path.join(model_folder, 'MVIMG')

                        # 检查图片是否为微视频
                        if is_mv_photo(file_path):
                            has_mvimg = True  # 找到至少一个微视频
                            if not os.path.exists(mvimg_folder):
                                os.makedirs(mvimg_folder)
                            shutil.move(file_path, os.path.join(mvimg_folder, file_name))
                            print(f'已移动 {file_name} 到 {mvimg_folder}')
                        else:
                            has_img = True  # 找到至少一张普通图片
                            if not os.path.exists(img_folder):
                                os.makedirs(img_folder)
                            shutil.move(file_path, os.path.join(img_folder, file_name))
                            print(f'已移动 {file_name} 到 {img_folder}')
                    else:
                        print(f'跳过 {file_name} (未找到制造商/型号信息)')

                except Exception as e:
                    print(f'处理 {file_name} 时出错: {e}')

            # 处理视频
            elif ext in ('mp4', 'mov', 'avi', 'mkv'):
                try:
                    metadata = get_video_metadata_ffprobe(file_path)
                    manufacturer = extract_metadata_field(metadata, 'com.android.manufacturer')
                    model = extract_metadata_field(metadata, 'com.android.model') or extract_metadata_field(metadata, 'com.xiaomi.product.marketname')

                    # 清理制造商和型号名称
                    manufacturer = sanitize_folder_name(manufacturer)
                    model = sanitize_folder_name(model)

                    # 仅在找到制造商和型号时继续处理
                    if manufacturer and model:
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, model)
                        vid_folder = os.path.join(model_folder, 'VID')

                        has_vid = True  # 找到至少一个视频
                        if not os.path.exists(vid_folder):
                            os.makedirs(vid_folder)
                        shutil.move(file_path, os.path.join(vid_folder, file_name))
                        print(f'已移动 {file_name} 到 {vid_folder}')
                    else:
                        print(f'跳过 {file_name} (未找到制造商/型号信息)')
                except Exception as e:
                    print(f'处理 {file_name} 时出错: {e}')

            else:
                print(f'跳过非图片/视频文件: {file_name}')

            # 仅在移动至少一个文件时创建文件夹
            if has_img or has_mvimg or has_vid:
                if has_img and not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                if has_mvimg and not os.path.exists(mvimg_folder):
                    os.makedirs(mvimg_folder)
                if has_vid and not os.path.exists(vid_folder):
                    os.makedirs(vid_folder)

# 示例用法：
source_directory = r"F:\PhotoClassification\Me\1"
destination_directory = r"F:\PhotoClassification\Me\3"
organize_files_by_device(source_directory, destination_directory)



