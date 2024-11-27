import os
import shutil
import hashlib
import sys
import io
import re

# 设置 stdout 为 utf-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def calculate_file_hash(file_path, hash_algo='md5'):
    """计算文件的 MD5 哈希值"""
    hash_func = hashlib.new(hash_algo)
    try:
        with open(file_path, 'rb') as f:
            # 逐块读取文件进行哈希计算
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def extract_hash_from_filename(filename, hash_length=32):
    """从文件名中提取哈希值部分"""
    # 提取文件名的哈希部分，假设哈希部分是由32个字符（MD5长度）组成
    # 用正则表达式提取文件名开头的哈希部分，忽略 Id_* 后缀
    match = re.match(r"([a-f0-9]{32})", filename.split('.')[0], re.IGNORECASE)
    if match:
        return match.group(1)  # 返回匹配的哈希部分
    return None

def move_files(src_directory, dest_directory, hash_algo='md5'):
    # 遍历目录下的所有文件和子文件夹
    for root, _, files in os.walk(src_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # 计算文件的 MD5 哈希值
            file_hash = calculate_file_hash(file_path, hash_algo)
            if not file_hash:
                continue  # 如果无法计算哈希，跳过该文件

            # 提取文件名中的哈希部分
            filename_hash_prefix = extract_hash_from_filename(filename)
            
            if not filename_hash_prefix:
                continue  # 如果文件名中没有找到有效的哈希部分，跳过该文件

            # 输出文件名和哈希值
            try:
                print(f"File: {filename}, Hash: {file_hash}")
            except UnicodeEncodeError:
                # 如果遇到编码错误，跳过该打印语句
                print(f"File: {filename} (contains non-printable characters)")

            # 完全匹配文件的哈希值
            if file_hash == filename_hash_prefix:  # 如果哈希值完全匹配
                # 计算目标路径，保留目录结构
                relative_path = os.path.relpath(root, src_directory)
                dest_path = os.path.join(dest_directory, relative_path)
                os.makedirs(dest_path, exist_ok=True)
                
                # 移动文件到目标目录
                shutil.move(file_path, os.path.join(dest_path, filename))
                
                try:
                    print(f"Moved file {file_path} to {dest_path}")
                except UnicodeEncodeError:
                    pass  # 如果遇到编码错误，跳过该打印语句

# 示例：扫描 E:\test，并将哈希匹配的文件移动到 E:\test1
src_directory = r"E:\Root"
dest_directory = r"E:\Root1"
move_files(src_directory, dest_directory)
