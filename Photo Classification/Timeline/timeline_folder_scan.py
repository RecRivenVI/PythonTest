import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# PhotoClassification的根路径
base_dir = r"F:\PhotoClassification"

# 文件夹列表初始化
folders = []

# 自动扫描文件夹生成路径列表
def generate_folder_list(base_dir):
    print("开始扫描文件夹...")
    for user_folder in ['Mom', 'Me']:  # 假设根目录下只有这两个文件夹
        user_path = os.path.join(base_dir, user_folder, 'Categorized', 'MiuiCamera')
        print(f"检查用户文件夹: {user_path}")
        if os.path.exists(user_path):
            print(f"找到文件夹: {user_path}")
            # 遍历MiuiCamera下的设备文件夹
            for device_folder in os.listdir(user_path):
                img_path = os.path.join(user_path, device_folder, 'IMG')
                mvimg_path = os.path.join(user_path, device_folder, 'MVIMG')
                vid_path = os.path.join(user_path, device_folder, 'VID')
                # 检查并添加 IMG 文件夹路径
                if os.path.exists(img_path):
                    folders.append(img_path)
                    print(f"添加文件夹: {img_path}")
                else:
                    print(f"未找到文件夹: {img_path}")

                # 检查并添加 MVIMG 文件夹路径
                if os.path.exists(mvimg_path):
                    folders.append(mvimg_path)
                    print(f"添加文件夹: {mvimg_path}")
                else:
                    print(f"未找到文件夹: {mvimg_path}")

                # 检查并添加 VID 文件夹路径
                if os.path.exists(vid_path):
                    folders.append(vid_path)
                    print(f"添加文件夹: {vid_path}")
                else:
                    print(f"未找到文件夹: {vid_path}")
        else:
            print(f"未找到用户文件夹: {user_path}")

# 执行自动扫描
generate_folder_list(base_dir)

# 文件路径输出为文本文档
output_file = os.path.join(current_dir, 'timeline_folder_paths.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    for folder in folders:
        f.write(f"{folder}\n")

print(f"文件夹路径已保存到: {output_file}")
