import os
import zipfile
import struct
from datetime import datetime, timezone

def parse_extended_timestamp(extra):
    """
    解析 ZIP 扩展字段中的 mtime (0x5455 Extended Timestamp)
    返回 UTC 时间戳或 None
    """
    i = 0
    while i + 4 <= len(extra):
        header_id, data_size = struct.unpack("<HH", extra[i:i+4])
        data = extra[i+4:i+4+data_size]
        i += 4 + data_size

        if header_id == 0x5455:  # Extended Timestamp
            # 第一个字节是 flags，bit0 表示 mtime 存在
            flags = data[0]
            if flags & 0x01:
                # 后续 4 字节为 mtime (Unix 时间戳, UTC)
                mtime, = struct.unpack("<I", data[1:5])
                return mtime
    return None

def update_zip_timestamp(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        times = []
        for info in zf.infolist():
            # 先尝试解析扩展字段 mtime
            mtime = parse_extended_timestamp(info.extra)
            if mtime is not None:
                # 转换为系统本地时区
                dt = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone()
            else:
                # 回退到 DOS 时间（已是本地时区）
                dt = datetime(*info.date_time)

            times.append(dt)

        if not times:
            print(f"{zip_path} 内没有文件，跳过。")
            return

        # 找到最晚的修改时间
        latest_time = max(times)
        print(f"{zip_path} 内最晚修改时间 (本地时区): {latest_time}")

        # 转换为时间戳（秒）
        ts = latest_time.timestamp()

        # 修改 zip 文件本身的访问时间和修改时间
        os.utime(zip_path, (ts, ts))
        print(f"已更新 {zip_path} 的时间戳为 {latest_time}")

if __name__ == "__main__":
    # 遍历当前目录下所有 zip 文件
    for fname in os.listdir("."):
        if fname.lower().endswith(".zip"):
            update_zip_timestamp(fname)