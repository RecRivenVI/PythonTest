import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk

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

def sanitize_folder_name(name):
    """Sanitize folder name by replacing invalid characters with a single space and remove trailing/leading spaces."""
    sanitized_name = re.sub(r'[^\w\s-]', ' ', name)  # Replace invalid characters with a space
    return sanitized_name.strip()  # Remove leading and trailing spaces

def organize_files_by_device(source_dir, destination_dir, log_area):
    """Organize images and videos by manufacturer and model."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        log_area.insert(tk.END, f'Processing directory: {root}\n')  # Log current directory being processed
        log_area.see(tk.END)  # Scroll to the end of the text area
        for file_name in files:
            file_path = os.path.join(root, file_name)
            ext = file_name.lower().split('.')[-1]  # Check file extension in a case-insensitive way

            # Process images
            if ext in ('jpg', 'jpeg', 'png', 'tiff', 'bmp'):  # Add other supported formats as needed
                try:
                    exif = get_exif_data(file_path)
                    if 'Make' in exif and 'Model' in exif:
                        manufacturer = sanitize_folder_name(exif['Make'].replace(" ", "_"))
                        camera_model = sanitize_folder_name(exif['Model'].replace(" ", "_"))

                        # Create folder paths for manufacturer and model
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, camera_model)

                        # Create directories if they don't exist
                        os.makedirs(manufacturer_folder, exist_ok=True)
                        os.makedirs(model_folder, exist_ok=True)

                        # Move the file to the model folder
                        shutil.move(file_path, os.path.join(model_folder, file_name))
                        log_area.insert(tk.END, f'Moved {file_name} to {model_folder}\n')
                    else:
                        log_area.insert(tk.END, f'Skipped {file_name} (no manufacturer/model info)\n')
                except Exception as e:
                    log_area.insert(tk.END, f'Error processing {file_name}: {e}\n')

            # Process videos
            elif ext in ('mp4', 'mov', 'avi', 'mkv'):
                try:
                    metadata = get_video_metadata_ffprobe(file_path)

                    manufacturer = extract_metadata_field(metadata, 'com.android.manufacturer')
                    model = extract_metadata_field(metadata, 'com.android.model') or extract_metadata_field(metadata, 'com.xiaomi.product.marketname')

                    if manufacturer and model:
                        manufacturer = sanitize_folder_name(manufacturer.replace(" ", "_"))
                        model = sanitize_folder_name(model.replace(" ", "_"))

                        # Create folder paths based on manufacturer and model
                        manufacturer_folder = os.path.join(destination_dir, manufacturer)
                        model_folder = os.path.join(manufacturer_folder, model)

                        os.makedirs(manufacturer_folder, exist_ok=True)
                        os.makedirs(model_folder, exist_ok=True)

                        # Move video to the appropriate folder
                        shutil.move(file_path, os.path.join(model_folder, file_name))
                        log_area.insert(tk.END, f'Moved {file_name} to {model_folder}\n')
                    else:
                        log_area.insert(tk.END, f'Skipped {file_name} (no manufacturer/model info)\n')
                except Exception as e:
                    log_area.insert(tk.END, f'Error processing {file_name}: {e}\n')
            else:
                log_area.insert(tk.END, f'Skipped non-image/video file: {file_name}\n')

def start_processing(source_dir, destination_dir, log_area):
    """Start the file organizing process."""
    log_area.delete(1.0, tk.END)  # Clear previous logs
    organize_files_by_device(source_dir, destination_dir, log_area)

def browse_source(log_area):
    """Browse and select the source directory."""
    source_dir = filedialog.askdirectory()
    if source_dir:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, source_dir)

def browse_destination(log_area):
    """Browse and select the destination directory."""
    destination_dir = filedialog.askdirectory()
    if destination_dir:
        destination_entry.delete(0, tk.END)
        destination_entry.insert(0, destination_dir)

# Create the main window
root = tk.Tk()
root.title("File Organizer")
root.geometry("600x400")  # Set initial window size

# Create input fields
source_label = ttk.Label(root, text="Source Directory:")
source_label.pack(pady=5)

source_entry = ttk.Entry(root, width=50)
source_entry.pack(pady=5)

source_button = ttk.Button(root, text="Browse", command=lambda: browse_source(log_area))
source_button.pack(pady=5)

destination_label = ttk.Label(root, text="Destination Directory:")
destination_label.pack(pady=5)

destination_entry = ttk.Entry(root, width=50)
destination_entry.pack(pady=5)

destination_button = ttk.Button(root, text="Browse", command=lambda: browse_destination(log_area))
destination_button.pack(pady=5)

# Create log area
log_area = scrolledtext.ScrolledText(root, width=70, height=15)
log_area.pack(pady=5)

# Create start button
start_button = ttk.Button(root, text="Start", command=lambda: start_processing(source_entry.get(), destination_entry.get(), log_area))
start_button.pack(pady=5)

# Create exit button
exit_button = ttk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=5)

# Resize elements when the window is resized
def on_resize(event):
    log_area.config(width=int(event.width * 0.9), height=int(event.height * 0.6))
    source_entry.config(width=int(event.width * 0.4))
    destination_entry.config(width=int(event.width * 0.4))

root.bind('<Configure>', on_resize)

root.mainloop()
