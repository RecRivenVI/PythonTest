import os
import zipfile
import struct
from datetime import datetime, timezone

def parse_extended_timestamp(extra):
    """
    解析 ZIP/JAR 扩展字段中的 mtime (0x5455 Extended Timestamp)
    返回 UTC 时间戳或 None
    """
    i = 0
    while i + 4 <= len(extra):
        header_id, data_size = struct.unpack("<HH", extra[i:i+4])
        data = extra[i+4:i+4+data_size]
        i += 4 + data_size

        if header_id == 0x5455:  # Extended Timestamp
            flags = data[0]
            if flags & 0x01:
                mtime, = struct.unpack("<I", data[1:5])
                return mtime
    return None

def update_archive_timestamp(archive_path):
    """
    更新 ZIP/JAR 文件的时间戳为其内部最新文件的修改时间
    """
    with zipfile.ZipFile(archive_path, 'r') as zf:
        times = []
        for info in zf.infolist():
            mtime = parse_extended_timestamp(info.extra)
            if mtime is not None:
                dt = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone()
            else:
                dt = datetime(*info.date_time)
            times.append(dt)

        if not times:
            print(f"{archive_path} 内没有文件，跳过。")
            return

        latest_time = max(times)
        print(f"{archive_path} 内最晚修改时间 (本地时区): {latest_time}")

        ts = latest_time.timestamp()
        os.utime(archive_path, (ts, ts))
        print(f"已更新 {archive_path} 的时间戳为 {latest_time}")

if __name__ == "__main__":
    # 遍历当前目录下所有 JAR/ZIP 文件
    for fname in os.listdir("."):
        if fname.lower().endswith((".jar", ".zip")):
            update_archive_timestamp(fname)
