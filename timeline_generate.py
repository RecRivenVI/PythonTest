import subprocess

# 定义要执行的脚本
scripts = [
    'timeline_folder_scan.py',
    'timeline_data_create.py',
    'timeline_data_render.py'
]

# 按顺序执行每个脚本
for script in scripts:
    try:
        print(f"正在执行 {script} ...")
        result = subprocess.run(['python', script], check=True)
        print(f"{script} 执行成功！")
    except subprocess.CalledProcessError as e:
        print(f"执行 {script} 时出错: {e}")
        break
