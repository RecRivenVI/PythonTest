import os
import re
from PIL import Image
from PIL.ExifTags import TAGS

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

def sanitize_name(name):
    """Sanitize the device name by replacing invalid characters with a space."""
    return re.sub(r'[^\w\s-]', ' ', name).strip()  # Replace invalid characters with spaces and remove extra spaces

def extract_device_info(source_dir, output_file):
    """Extract all device manufacturer and model information from images and write them to a text file."""
    device_info = set()  # Use a set to store unique (manufacturer, model) pairs

    # Use os.walk() to recursively traverse the directory tree
    for root, dirs, files in os.walk(source_dir):
        print(f'Processing directory: {root}')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]
            if ext in ('jpg', 'jpeg', 'png', 'tiff', 'bmp'):  # Check if file is an image
                try:
                    exif = get_exif_data(file_path)

                    # Extract Manufacturer and Model if available
                    manufacturer = exif.get('Make', 'Unknown Manufacturer')
                    model = exif.get('Model', 'Unknown Model')

                    # Sanitize names
                    manufacturer = sanitize_name(manufacturer)
                    model = sanitize_name(model)

                    # Add to the set to avoid duplicates
                    device_info.add((manufacturer, model))
                except Exception as e:
                    print(f'Error processing {file_name}: {e}')

    # Write the device information to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for manufacturer, model in sorted(device_info):
            f.write(f'Manufacturer: {manufacturer}, Model: {model}\n')

    print(f'Device information successfully written to {output_file}')

# Example usage:
source_directory = r'E:\照片分类'
output_txt = 'E:/device_info.txt'
extract_device_info(source_directory, output_txt)
