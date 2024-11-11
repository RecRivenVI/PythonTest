import os
import pyexiv2
import csv

# 文件夹路径
input_file = "timeline_watermark_path.txt"  # 输入文件路径
output_file = "photos_with_lenswatermark.csv"  # 输出文件名

# 创建输出文件并写入
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # 写入CSV文件的标题
    csv_writer.writerow(["文件名称", "拍摄时间", "设备型号", "用户", "文件类型"])

    # 读取文件夹路径
    with open(input_file, 'r', encoding='utf-8') as f:
        for folder_path in f:
            folder_path = folder_path.strip()  # 去掉多余的空格和换行
            
            # 遍历文件夹中的所有文件
            for filename in os.listdir(folder_path):
                # 构造完整的文件路径
                file_path = os.path.join(folder_path, filename)

                # 检查文件是否为图像文件（根据扩展名）
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                    try:
                        # 打开图片文件
                        img = pyexiv2.Image(file_path)

                        # 读取 XMP 元数据
                        xmp_data = img.read_xmp()

                        # 获取拍摄时间
                        capture_time = str(xmp_data.get('Xmp.exif.DateTimeOriginal', ''))

                        # 获取设备型号（假设从文件路径中提取）
                        device_model = folder_path.split(os.sep)[-2]  # 从路径中获取设备型号
                        user = folder_path.split(os.sep)[-3]  # 从路径中获取用户（自己或老妈）

                        # 判断文件类型
                        file_type = "动态照片" if "MVIMG" in folder_path else "照片"

                        # 检查是否包含 lenswatermark 标签
                        if any('<lenswatermark' in str(value) for value in xmp_data.values()):
                            # 如果不包含，写入文件信息到CSV
                            csv_writer.writerow([filename, capture_time, device_model, user, file_type])

                        # 关闭图片文件
                        img.close()
                    
                    except Exception as e:
                        print(f"无法读取 {filename}: {e}")

print(f"输出已保存到 {output_file}。")
