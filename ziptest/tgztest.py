import os
import tarfile
from datetime import datetime, timezone

def update_tgz_timestamp(tgz_path):
    with tarfile.open(tgz_path, 'r:gz') as tf:
        times = []
        for info in tf.getmembers():
            # tarfile 的 mtime 就是 Unix 时间戳 (UTC)
            if info.mtime:
                dt = datetime.fromtimestamp(info.mtime, tz=timezone.utc).astimezone()
                times.append(dt)

        if not times:
            print(f"{tgz_path} 内没有文件，跳过。")
            return

        # 找到最晚的修改时间
        latest_time = max(times)
        print(f"{tgz_path} 内最晚修改时间 (本地时区): {latest_time}")

        # 转换为时间戳（秒）
        ts = latest_time.timestamp()

        # 修改 tgz 文件本身的访问时间和修改时间
        os.utime(tgz_path, (ts, ts))
        print(f"已更新 {tgz_path} 的时间戳为 {latest_time}")

if __name__ == "__main__":
    # 遍历当前目录下所有 tgz 文件
    for fname in os.listdir("."):
        if fname.lower().endswith(".tgz"):
            update_tgz_timestamp(fname)
