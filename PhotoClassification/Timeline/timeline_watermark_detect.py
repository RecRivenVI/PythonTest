import os
import csv
import xml.etree.ElementTree as ET
from PIL import Image
from PIL.ExifTags import TAGS

import os
import xml.etree.ElementTree as ET

def extract_xmp(file_path):
    """Extract XMP data from the image file."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

            # 寻找 XMP 数据
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')

            if start == -1 or end == -1:
                print(f"XMP meta not found in {file_path}.")  # 未找到 XMP 数据
                return None
            
            # 提取并解码 XMP 数据
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')

            return xmp_string

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def has_lens_watermark(file_path):
    """Check if the lens watermark is present in the photo."""
    xmp_data = extract_xmp(file_path)
    if xmp_data:
        # 查找 lenswatermark 字段
        if '<lenswatermark' in xmp_data:
            print(f"Lens watermark found in {file_path}.")  # 找到水印
            return False
        else:
            print(f"No lens watermark in {file_path}.")  # 没有水印
            return True
    return True  # XMP 数据不存在时，认为没有水印

    
def extract_exif(photo_path):
    """Extract EXIF data from the image file."""
    try:
        image = Image.open(photo_path)
        exif_data = image._getexif() or {}
        
        # 通过 TAGS 提取可读标签
        readable_exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
        return readable_exif
    except Exception as e:
        print(f"Error extracting EXIF from {photo_path}: {e}")
        return None

def extract_photo_info(photo_path):
    """Extract photo information from the image file."""
    try:
        with open(photo_path, 'rb') as f:
            data = f.read()

            # Find XMP data
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')

            if start != -1 and end != -1:
                # Extract XMP data and decode
                xmp_data = data[start:end]
                xmp_string = xmp_data.decode('utf-8', errors='ignore')

                # Check for lenswatermark
                if not has_lens_watermark(photo_path):
                    # Get photo information (file name, timestamp, device model, user, file type)
                    file_name = os.path.basename(photo_path)
                    timestamp = extract_timestamp(photo_path)  # You can implement this function as needed
                    device_model = extract_device_model(photo_path)  # You can implement this function as needed
                    user = extract_user(photo_path)  # You can implement this function as needed
                    file_type = "动态照片" if 'MVIMG' in photo_path else "照片"

                    return [file_name, timestamp, device_model, user, file_type]

    except Exception as e:
        print(f"Error processing file {photo_path}: {e}")
    
    return None
def extract_timestamp(photo_path):
    """Extract timestamp from the photo. Placeholder function."""
    exif_data = extract_exif(photo_path)
    if exif_data and 'DateTime' in exif_data:
        return exif_data['DateTime']
    return "Unknown"  # Replace with actual timestamp if available

def extract_device_model(photo_path):
    """Extract device model from the path. Placeholder function."""
    # You can parse the path to find the device model if needed
    model_segment = photo_path.split('\\')[-3]  # Assuming device model is in a specific position
    return model_segment if model_segment else "Unknown"

def extract_user(photo_path):
    """Extract user from the path. Placeholder function."""
    if "老妈" in photo_path:
        return "老妈"
    else:
        return "自己"

def process_photos(photo_paths):
    output_rows = []

    for path in photo_paths:
        print(f"Processing path: {path}")  # 打印当前处理的路径
        try:
            # Get list of image files in the directory
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg')):
                        file_path = os.path.join(root, file)
                        print(f"Checking file: {file_path}")  # 打印文件路径
                        # 调用你的检查函数
                        if not has_lens_watermark(file_path):  
                            timestamp = extract_timestamp(file_path)  # 提取拍摄时间
                            device_model = extract_device_model(file_path)  # 提取设备型号
                            user = extract_user(file_path)  # 根据路径确定用户
                            file_type = "照片" if "IMG" in root else "动态照片"  # 根据文件夹确定文件类型
                            output_rows.append([file, timestamp, device_model, user, file_type])
        except Exception as e:
            print(f"Error processing path {path}: {e}")

    return output_rows

def main():
    # Read paths from the text file
    try:
        with open('timeline_folder_paths.txt', 'r', encoding='utf-8') as f:
            photo_paths = [line.strip() for line in f if line.strip()]

        print(f"Found {len(photo_paths)} paths to process.")  # 打印找到的路径数量

        # Process photos
        output_rows = process_photos(photo_paths)

        # Write results to CSV
        if output_rows:
            with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['文件名称', '拍摄时间', '设备型号', '用户', '文件类型'])  # Header
                writer.writerows(output_rows)
            print(f"Output written to 'output.csv' with {len(output_rows)} records.")  # 输出记录数量
        else:
            print("No records found without lens watermark.")
    except Exception as e:
        print(f"Error reading paths: {e}")

if __name__ == "__main__":
    main()
