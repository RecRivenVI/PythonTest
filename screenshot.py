import os
import shutil
from PIL import Image

# 原始截图文件夹路径
source_folder = r'F:\PhotoClassification\Me\Categorized\屏幕截图'
# 目标分类文件夹路径
destination_folder = r'F:\PhotoClassification\Me\Categorized\屏幕截图分类'

# 创建按分辨率分类的文件夹
def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 遍历原始文件夹中的图片
def classify_images_by_resolution(source, destination):
    for filename in os.listdir(source):
        # 获取完整文件路径
        file_path = os.path.join(source, filename)
        
        # 检查文件是否是图片格式
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            try:
                # 打开图片并获取分辨率
                with Image.open(file_path) as img:
                    width, height = img.size
                
                # 确定分辨率组，将较小的值作为宽，较大的值作为高
                min_res, max_res = sorted([width, height])
                resolution_folder = f'{min_res}x{max_res}'
                
                # 创建对应分辨率的文件夹
                target_folder = os.path.join(destination, resolution_folder)
                create_folder(target_folder)
                
                # 将图片移动到对应分辨率的文件夹中
                shutil.move(file_path, os.path.join(target_folder, filename))
                print(f'已将 {filename} 移动到 {target_folder}')
            
            except Exception as e:
                print(f'处理 {filename} 时出错: {e}')

# 运行分类函数
classify_images_by_resolution(source_folder, destination_folder)
