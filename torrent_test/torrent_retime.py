import os
import bencodepy
from datetime import datetime, timezone

def sync_torrent_timestamp(torrent_path):
    print(f"--- 处理: {torrent_path} ---")
    
    try:
        with open(torrent_path, 'rb') as f:
            raw_data = f.read()
            metadata = bencodepy.decode(raw_data)
    except Exception as e:
        print(f"❌ 读取或解码失败: {e}")
        return

    # 获取创建时间 (key 是 b'creation date')
    # 这是一个 Unix 时间戳 (整数)
    creation_timestamp = metadata.get(b'creation date')

    if creation_timestamp:
        # 为了显示给用户看，转换为本地时间
        dt = datetime.fromtimestamp(creation_timestamp, tz=timezone.utc).astimezone()
        print(f"✅ 找到内部创建时间: {dt}")

        try:
            # os.utime 接受 (访问时间, 修改时间) 的元组
            # 直接使用原始的 Unix 时间戳是最准确的，不需要手动处理时区转换
            os.utime(torrent_path, (creation_timestamp, creation_timestamp))
            print(f"🚀 已将文件修改时间更新为: {dt}")
        except Exception as e:
            print(f"❌ 修改文件时间失败: {e}")
    else:
        print("⚠️ 该种子文件内部没有 'creation date' 字段，跳过。")

if __name__ == "__main__":
    # 检查当前目录下是否有 .torrent 文件
    found = False
    for fname in os.listdir("."):
        if fname.lower().endswith(".torrent"):
            found = True
            sync_torrent_timestamp(fname)
            print("-" * 30)
    
    if not found:
        print("当前目录下没有找到 .torrent 文件。")