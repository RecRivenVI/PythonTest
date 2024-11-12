import subprocess
from datetime import datetime, timedelta
import pytz
import os

# 获取视频的创建时间
def get_video_taken_time(video_path):
    try:
        # 指定 ffprobe 完整路径
        ffprobe_path = r"C:\Users\RecRivenVI\Downloads\FFmpeg\bin\ffprobe.exe"  # 请确保这里是你实际的 ffprobe 路径

        # 获取创建时间
        cmd_creation_time = [
            ffprobe_path,  # 使用完整路径
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'format_tags=creation_time',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        creation_time_output = subprocess.check_output(cmd_creation_time).decode().strip()

        if creation_time_output:
            # 解析 creation_time 为 datetime 对象
            creation_time = datetime.strptime(creation_time_output, '%Y-%m-%dT%H:%M:%S.%fZ')
            
            # 获取视频时长
            cmd_duration = [
                ffprobe_path,  # 使用完整路径
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            duration_output = subprocess.check_output(cmd_duration).decode().strip()
            duration = float(duration_output)  # 视频时长，单位为秒

            # 计算实际拍摄时间 = 创建时间 - 视频时长
            adjusted_time = creation_time - timedelta(seconds=duration)

            # 如果你需要进行时区转换
            tz = pytz.timezone('Asia/Shanghai')  # 设置为北京时间
            local_time = adjusted_time.replace(tzinfo=pytz.utc).astimezone(tz)

            return local_time, duration
        else:
            print(f"视频 {video_path} 缺少 creation_time 信息")
    except Exception as e:
        print(f"无法读取视频 {video_path} 的拍摄时间: {e}")
    return None, None

# 修改文件的创建时间和修改时间
def modify_file_times(file_path, new_creation_time, new_modification_time):
    try:
        # 将 datetime 对象转换为时间戳
        creation_timestamp = new_creation_time.timestamp()
        modification_timestamp = new_modification_time.timestamp()

        # 修改文件的访问时间和修改时间
        os.utime(file_path, (modification_timestamp, modification_timestamp))

        # 设置文件的创建时间为指定的时间（注意：Windows 可能不支持直接修改创建时间）
        # Windows 不能通过 os.utime 修改创建时间，但可以通过以下方法使用 PowerShell 脚本来修改
        import subprocess
        cmd = f"powershell -Command \"$(Get-Item '{file_path}').CreationTime = '{new_creation_time.strftime('%Y-%m-%d %H:%M:%S')}'\""
        subprocess.run(cmd, shell=True)
        
        print(f"文件时间已修改：创建时间: {new_creation_time}, 修改时间: {new_modification_time}")
    except Exception as e:
        print(f"无法修改文件时间: {e}")

# 遍历指定目录及其子目录中的所有文件
def process_video_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 只处理视频文件，可以根据需要调整文件扩展名
            if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                video_file_path = os.path.join(root, file)

                # 获取视频的拍摄时间和视频时长
                video_taken_time, video_duration = get_video_taken_time(video_file_path)

                if video_taken_time and video_duration is not None:
                    # 设置创建时间为视频拍摄时间
                    new_creation_time = video_taken_time

                    # 设置修改时间为视频拍摄时间 + 视频时长
                    new_modification_time = video_taken_time + timedelta(seconds=video_duration)

                    # 修改文件的时间
                    modify_file_times(video_file_path, new_creation_time, new_modification_time)
                else:
                    print(f"无法获取视频 {video_file_path} 的拍摄时间，文件时间未修改。")

# 调用函数处理指定目录
process_video_files_in_directory(r"G:\Backups\Camera")
