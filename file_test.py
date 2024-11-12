from PIL import Image
import os
import shutil

# 增加 Pillow 允许的最大图像像素数
Image.MAX_IMAGE_PIXELS = 1000000000  # 设置为更大的值，例：10亿个像素

# 增加解压缩炸弹宽容度
Image.MAX_DECOMPRESSION_PIXELS = 1000000000  # 设置更高的解压缩限制

# 定义常见图片扩展名
COMMON_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

def is_image_file(file_path):
    try:
        # 尝试打开文件以确认它是否为图片
        with Image.open(file_path) as img:
            img.verify()  # 验证图像文件完整性
            return True
    except (IOError, SyntaxError, ValueError, Image.DecompressionBombError):
        # 如果文件无法打开、不是图片，或格式不受支持，或者触发解压缩炸弹错误，返回 False
        return False

def move_image_files(src_directory, dest_directory):
    # 遍历目录下的所有文件和子文件夹
    for root, _, files in os.walk(src_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            
            if os.path.isfile(file_path) and file_extension in COMMON_IMAGE_EXTENSIONS:
                # 检查文件是否为图片
                if is_image_file(file_path):
                    # 计算目标路径，保留目录结构
                    relative_path = os.path.relpath(root, src_directory)
                    dest_path = os.path.join(dest_directory, relative_path)
                    os.makedirs(dest_path, exist_ok=True)
                    
                    # 移动文件到目标目录
                    shutil.move(file_path, os.path.join(dest_path, filename))
                    
                    # 捕获并跳过无法编码的字符
                    try:
                        print(f"Moved image file {file_path} to {dest_path}")
                    except UnicodeEncodeError:
                        pass  # 如果遇到编码错误，跳过该打印语句

# 示例：扫描 E:\test，并将识别为图片的文件移动到 E:\test1
src_directory = r"E:\Root"
dest_directory = r"E:\Root1"
move_image_files(src_directory, dest_directory)
