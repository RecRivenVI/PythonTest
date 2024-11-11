import os
import re
import subprocess
import shutil

EXIFTOOL_PATH = r"D:\Github\PythonTest\exiftool-12.98_64\exiftool.exe"

def get_exif_data_exiftool(file_path):
    """Extract EXIF data using ExifTool."""
    try:
        cmd = [EXIFTOOL_PATH, '-j', file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        metadata = result.stdout
        return metadata
    except Exception as e:
        print(f"Error running ExifTool for {file_path}: {e}")
        return None

def extract_metadata_field(metadata, field_name):
    """Extract specific field from metadata."""
    match = re.search(f'"{field_name}": "(.*?)"', metadata)
    if match:
        return match.group(1).strip()
    return None

def sanitize_folder_name(name):
    """Sanitize folder name by removing leading/trailing spaces and null characters."""
    return re.sub(r'\0', ' ', name).strip()  # Remove null characters and trim spaces

def organize_heif_files(source_dir, destination_dir):
    """Organize HEIF images by manufacturer and model."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        print(f'Processing directory: {root}')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]

            # Only process HEIF files
            if ext in ('heic', 'heif'):
                try:
                    metadata = get_exif_data_exiftool(file_path)
                    if metadata:
                        manufacturer = extract_metadata_field(metadata, 'Make')
                        camera_model = extract_metadata_field(metadata, 'Model')

                        # Sanitize manufacturer and model names
                        manufacturer = sanitize_folder_name(manufacturer)
                        camera_model = sanitize_folder_name(camera_model)

                        # Only proceed if manufacturer and model are found
                        if manufacturer and camera_model:
                            manufacturer_folder = os.path.join(destination_dir, manufacturer)
                            model_folder = os.path.join(manufacturer_folder, camera_model)
                            img_folder = os.path.join(model_folder, 'IMG')

                            # Create necessary folders
                            if not os.path.exists(img_folder):
                                os.makedirs(img_folder)

                            # Move the file to the correct folder
                            shutil.move(file_path, os.path.join(img_folder, file_name))
                            print(f'Moved {file_name} to {img_folder}')
                        else:
                            print(f'Skipped {file_name} (no manufacturer/model info)')
                except Exception as e:
                    print(f'Error processing {file_name}: {e}')
            else:
                print(f'Skipped non-HEIF file: {file_name}')

# Example usage:
source_directory = r"C:\Users\RecRivenVI\OneDrive\图片\载具"
destination_directory = r"C:\Users\RecRivenVI\OneDrive\图片\载具1"
organize_heif_files(source_directory, destination_directory)
