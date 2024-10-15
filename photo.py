import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import shutil

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

def sanitize_folder_name(name):
    """Sanitize folder name by replacing invalid characters with a single space and remove trailing/leading spaces."""
    sanitized_name = re.sub(r'[^\w\s-]', ' ', name)  # Replace invalid characters with a space
    return sanitized_name.strip()  # Remove leading and trailing spaces

def organize_photos_by_device_and_manufacturer(source_dir, destination_dir):
    """Organize photos into folders by manufacturer and camera model based on EXIF data."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Use os.walk() to recursively traverse the directory tree
    for root, dirs, files in os.walk(source_dir):
        print(f'Processing directory: {root}')  # Log current directory being processed
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]  # Check file extension in a case-insensitive way
            if ext in ('jpg', 'jpeg', 'png', 'tiff', 'bmp'):  # Add other supported formats as needed
                try:
                    exif = get_exif_data(file_path)
                    
                    # Check for Manufacturer and Model in EXIF data
                    if 'Make' in exif:
                        manufacturer = sanitize_folder_name(exif['Make'].replace(" ", "_"))
                    else:
                        manufacturer = 'Unknown_Manufacturer'
                    
                    if 'Model' in exif:
                        camera_model = sanitize_folder_name(exif['Model'].replace(" ", "_"))
                    else:
                        camera_model = 'Unknown_Model'

                    # Create folder paths for manufacturer and model
                    manufacturer_folder = os.path.join(destination_dir, manufacturer)
                    model_folder = os.path.join(manufacturer_folder, camera_model)

                    # Create directories if they don't exist
                    if not os.path.exists(manufacturer_folder):
                        os.makedirs(manufacturer_folder)
                    if not os.path.exists(model_folder):
                        os.makedirs(model_folder)

                    # Move the file to the model folder
                    shutil.move(file_path, os.path.join(model_folder, file_name))
                    print(f'Moved {file_name} to {model_folder}')
                    
                except Exception as e:
                    print(f'Error processing {file_name}: {e}')
            else:
                print(f'Skipped non-image file: {file_name}')  # Log skipped non-image files

# Example usage:
source_directory = r'D:\分类\#1未分类'
destination_directory = r'D:\分类\其他'
organize_photos_by_device_and_manufacturer(source_directory, destination_directory)