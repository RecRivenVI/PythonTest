import os
import subprocess

def extract_exif_data(input_dir, output_dir):
    # 遍历输入目录及子目录
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(input_file_path, input_dir)
            relative_path = os.path.splitext(relative_path)[0] + ".xml"  # 修改后缀为 .xml
            output_file_path = os.path.join(output_dir, relative_path)

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # 使用 exiftool 获取 EXIF 数据
            try:
                # 执行 exiftool 命令，使用 UTF-8 编码避免解码问题
                result = subprocess.run(
                    ['exiftool', '-X', input_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 遇到无法解码的字符时替换
                    check=True
                )

                # 获取输出内容
                exif_data = result.stdout.strip()

                # 如果 EXIF 数据为空，创建一个空文件
                if not exif_data:
                    print(f'Warning: No EXIF data for {input_file_path}. Writing empty file.')
                    exif_data = ''

                # 将 EXIF 数据保存为 XML 文件
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(exif_data)

            except subprocess.CalledProcessError as e:
                # 处理执行 exiftool 命令时的错误
                print(f'Error reading EXIF data from {input_file_path}: {e}')
                # 如果出错，创建一个空文件
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write('')

if __name__ == "__main__":
    input_dir = r"F:\PhotoClassification\整理#1"  # 替换为照片输入目录
    output_dir = r"F:\PhotoClassification\整理#1"  # 替换为输出目录
    extract_exif_data(input_dir, output_dir)
