import subprocess
import os
import shutil
import re

def get_video_metadata_ffprobe(video_path):
    """Extract video metadata using ffprobe."""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'default=noprint_wrappers=1', video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    metadata = result.stdout
    return metadata

def extract_metadata_field(metadata, field_name):
    """Extract specific field from metadata."""
    match = re.search(f'{field_name}=(.*)', metadata)
    if match:
        return match.group(1).strip()
    return None

def organize_videos_by_device_ffmpeg(source_dir, destination_dir):
    """Organize videos into folders based on metadata from ffprobe."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]
            if ext in ('mp4', 'mov', 'avi', 'mkv'):  # Supported formats
                try:
                    metadata = get_video_metadata_ffprobe(file_path)

                    manufacturer = extract_metadata_field(metadata, 'com.android.manufacturer') or 'Unknown_Manufacturer'
                    model = extract_metadata_field(metadata, 'com.android.model') or 'Unknown_Model'
                    market_name = extract_metadata_field(metadata, 'com.xiaomi.product.marketname') or model

                    # Create folder paths based on manufacturer and market name
                    manufacturer_folder = os.path.join(destination_dir, manufacturer)
                    model_folder = os.path.join(manufacturer_folder, market_name)

                    if not os.path.exists(manufacturer_folder):
                        os.makedirs(manufacturer_folder)
                    if not os.path.exists(model_folder):
                        os.makedirs(model_folder)

                    # Move video to the appropriate folder
                    shutil.move(file_path, os.path.join(model_folder, file_name))
                    print(f'Moved {file_name} to {model_folder}')
                
                except Exception as e:
                    print(f'Error processing {file_name}: {e}')
            else:
                print(f'Skipped non-video file: {file_name}')

# Example usage
source_directory = r'D:\Categorized\#1未分类'
destination_directory = r'D:\Categorized\其他'
organize_videos_by_device_ffmpeg(source_directory, destination_directory)