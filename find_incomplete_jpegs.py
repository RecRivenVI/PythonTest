import os

def find_problem_jpegs(folder_path):
    incomplete_files = []       # 以 FFD8 开头但不以 FFD9 结尾
    multiple_markers_files = [] # 文件中有多个 FFD8 或 FFD9

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg')):
                continue  # 只检查 jpg/jpeg 文件

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "rb") as f:
                    data = f.read()

                    # 只处理以 FFD8 开头的文件
                    if data[:2] != b'\xFF\xD8':
                        continue

                    # 检查结尾
                    ends_with_ffd9 = data[-2:] == b'\xFF\xD9'
                    if not ends_with_ffd9:
                        incomplete_files.append(file_path)

                    # 检查内部 FFD8 和 FFD9 出现次数
                    ffd8_count = data.count(b'\xFF\xD8')
                    ffd9_count = data.count(b'\xFF\xD9')

                    if ffd8_count > 1 or ffd9_count > 1:
                        multiple_markers_files.append({
                            "file": file_path,
                            "FFD8_count": ffd8_count,
                            "FFD9_count": ffd9_count
                        })

            except Exception as e:
                print(f"无法读取文件 {file_path}: {e}")

    return incomplete_files, multiple_markers_files

# 使用方法
folder = r"F:\PhotoSync\Pictures"  # 修改为你的文件夹路径
bad_files, multi_marker_files = find_problem_jpegs(folder)

print("以下文件以 FFD8 开头但不以 FFD9 结尾（可能损坏）:")
for f in bad_files:
    print(f)

print("\n以下文件内部存在多个 FFD8 或 FFD9:")
for info in multi_marker_files:
    print(f"{info['file']} - FFD8: {info['FFD8_count']} 次, FFD9: {info['FFD9_count']} 次")
