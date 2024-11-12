import subprocess
import os

def get_device_info(heic_file, exiftool_path):
    try:
        # 调用 exiftool 读取指定元数据字段
        result = subprocess.run([exiftool_path, "-Make", "-Model", heic_file], capture_output=True, text=True)
        
        # 如果调用失败，打印错误信息
        if result.returncode != 0:
            print(f"Error calling exiftool for file {heic_file}: {result.stderr}")
            return None, None
        
        output = result.stdout
        
        # 解析输出以提取设备信息
        manufacturer = ""
        model = ""
        for line in output.splitlines():
            if "Make" in line:
                manufacturer = line.split(":")[1].strip()
            elif "Model" in line:
                model = line.split(":")[1].strip()
        
        return manufacturer, model
    except Exception as e:
        print(f"Error reading metadata from {heic_file}: {e}")
        return None, None

# 扫描文件夹中的 HEIC 文件
exiftool_path = r"C:\Users\RecRivenVI\Downloads\exiftool-13.02_64\exiftool-13.02_64\exiftool.exe"
folder_path = r"F:\PhotoClassification\test"

for file_name in os.listdir(folder_path):
    if file_name.lower().endswith(".heic"):
        heic_file = os.path.join(folder_path, file_name)
        manufacturer, model = get_device_info(heic_file, exiftool_path)
        if manufacturer or model:
            print(f"File: {file_name}")
            print("Manufacturer:", manufacturer)
            print("Model:", model)
            print("-" * 30)
        else:
            print(f"No device info found for {file_name}.")
