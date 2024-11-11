import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import subprocess
import xml.etree.ElementTree as ET

# 提高解压缩图片像素限制，允许更大尺寸的图像
Image.MAX_IMAGE_PIXELS = None

def get_exif_data(image_path):
    """Extract EXIF data from an image."""
    image = Image.open(image_path)
    exif_data = image._getexif()  # Get EXIF data from image
    exif = {}

    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif[tag_name] = value
    return exif

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

def is_mv_photo(file_path):
    """Check if the photo is a Micro Video (MVIMG)."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

            # Find XMP data
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
            
            if start == -1 or end == -1:
                return False
            
            # Extract XMP data and decode
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')

            # Parse XML
            root = ET.fromstring(xmp_string)

            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'x': 'adobe:ns:meta/',
                'GCamera': 'http://ns.google.com/photos/1.0/camera/',
                'MiCamera': 'http://ns.xiaomi.com/photos/1.0/camera/'
            }

            description = root.find('.//rdf:Description', ns)

            # Check if rdf:Description was found
            if description is not None:
                micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                
                if micro_video == "1":
                    return True

            return False

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

def sanitize_folder_name(name):
    """Sanitize folder name by removing leading/trailing spaces and null characters."""
    return re.sub(r'\0', ' ', name).strip()  # Remove null characters and trim spaces

def organize_files_by_device(source_dir, destination_dir):
    """Organize images and videos by manufacturer and model."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        print(f'Processing directory: {root}')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]

            # Initialize flags for folder creation
            has_img = False
            has_mvimg = False
            has_vid = False

            # Process images
            if ext in ('jpg', 'jpeg', 'png', 'tiff', 'bmp'):
                try:
                    exif = get_exif_data(file_path)
                    manufacturer = sanitize_folder_name(exif.get('Make', ''))
                    camera_model = sanitize_folder_name(exif.get('Model', ''))

                    # Only proceed if manufacturer and model are found
                    if manufacturer and camera_model:
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, camera_model)

                        # Check if MVIMG or IMG folders should be created
                        img_folder = os.path.join(model_folder, 'IMG')
                        mvimg_folder = os.path.join(model_folder, 'MVIMG')

                        # Check if the image is a MVIMG
                        if is_mv_photo(file_path):
                            has_mvimg = True  # Found at least one MVIMG
                            if not os.path.exists(mvimg_folder):
                                os.makedirs(mvimg_folder)
                            shutil.move(file_path, os.path.join(mvimg_folder, file_name))
                            print(f'Moved {file_name} to {mvimg_folder}')
                        else:
                            has_img = True  # Found at least one regular image
                            if not os.path.exists(img_folder):
                                os.makedirs(img_folder)
                            shutil.move(file_path, os.path.join(img_folder, file_name))
                            print(f'Moved {file_name} to {img_folder}')
                    else:
                        print(f'Skipped {file_name} (no manufacturer/model info)')

                except Exception as e:
                    print(f'Error processing {file_name}: {e}')

            # Process videos
            elif ext in ('mp4', 'mov', 'avi', 'mkv'):
                try:
                    metadata = get_video_metadata_ffprobe(file_path)
                    manufacturer = extract_metadata_field(metadata, 'com.android.manufacturer')
                    model = extract_metadata_field(metadata, 'com.android.model') or extract_metadata_field(metadata, 'com.xiaomi.product.marketname')

                    # Sanitize manufacturer and model names
                    manufacturer = sanitize_folder_name(manufacturer)
                    model = sanitize_folder_name(model)

                    # Only proceed if manufacturer and model are found
                    if manufacturer and model:
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, model)
                        vid_folder = os.path.join(model_folder, 'VID')

                        has_vid = True  # Found at least one video
                        if not os.path.exists(vid_folder):
                            os.makedirs(vid_folder)
                        shutil.move(file_path, os.path.join(vid_folder, file_name))
                        print(f'Moved {file_name} to {vid_folder}')
                    else:
                        print(f'Skipped {file_name} (no manufacturer/model info)')
                except Exception as e:
                    print(f'Error processing {file_name}: {e}')

            else:
                print(f'Skipped non-image/video file: {file_name}')

            # Only create folders if at least one file has been moved
            if has_img or has_mvimg or has_vid:
                if has_img and not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                if has_mvimg and not os.path.exists(mvimg_folder):
                    os.makedirs(mvimg_folder)
                if has_vid and not os.path.exists(vid_folder):
                    os.makedirs(vid_folder)

# Example usage:
source_directory = r"F:\PhotoClassification\Me\Uncategorized"
destination_directory = r"F:\PhotoClassification\Me\Categorized"
organize_files_by_device(source_directory, destination_directory)