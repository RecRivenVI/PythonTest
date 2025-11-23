import os
import hashlib
import bencodepy
from datetime import datetime, timezone

def parse_torrent(torrent_path):
    print(f"--- 解析: {os.path.basename(torrent_path)} ---")
    
    try:
        with open(torrent_path, 'rb') as f:
            # 读取并解码 Bencode 数据
            raw_data = f.read()
            metadata = bencodepy.decode(raw_data)
    except Exception as e:
        print(f"读取失败: {e}")
        return

    # Bencode 解码后 key 和 value 都是 bytes 类型，需要根据情况 decode
    # 核心信息都在 'info' 字典里
    info = metadata.get(b'info', {})
    
    # 1. 获取种子名称 (Name)
    # 通常是建议的根文件夹名或文件名
    name = info.get(b'name', b'Unknown').decode('utf-8', errors='ignore')
    print(f"名称: {name}")

    # 2. 获取创建时间 (Creation Date)
    # 在根字典中，key 是 'creation date'
    creation_timestamp = metadata.get(b'creation date')
    if creation_timestamp:
        dt = datetime.fromtimestamp(creation_timestamp, tz=timezone.utc).astimezone()
        print(f"创建时间: {dt}")
    
    # 3. 获取创建者 (Created By) - 可选
    created_by = metadata.get(b'created by')
    if created_by:
        print(f"创建工具: {created_by.decode('utf-8', errors='ignore')}")

    # 4. 计算总大小和文件结构
    # Torrent 有两种模式：单文件 (Single File) 和 多文件 (Multi File)
    total_size = 0
    files_count = 0
    
    if b'files' in info:
        # --- 多文件模式 ---
        # info['files'] 是一个列表，每个元素包含 'length' 和 'path'
        print("模式: 多文件")
        for file_item in info[b'files']:
            length = file_item[b'length']
            total_size += length
            files_count += 1
            
            # path 是一个列表 (e.g. ['folder', 'subfolder', 'file.txt'])
            # path_list = [p.decode('utf-8', errors='ignore') for p in file_item[b'path']]
            # print(f"  - {'/'.join(path_list)} ({format_size(length)})") # 如果想打印所有文件取消注释
    else:
        # --- 单文件模式 ---
        # 直接读取 info['length']
        print("模式: 单文件")
        total_size = info.get(b'length', 0)
        files_count = 1

    print(f"文件数量: {files_count}")
    print(f"总大小: {format_size(total_size)}")

    # 5. 计算 Info Hash (磁力链接的核心)
    # 磁力链接的哈希是 info 字典部分的 SHA1 哈希值（必须对原始 bencode 字节流进行哈希）
    # 我们需要把解码后的 info 字典重新 encode 回去，或者截取原始数据
    info_bytes = bencodepy.encode(info)
    info_hash = hashlib.sha1(info_bytes).hexdigest().upper()
    print(f"Info Hash: {info_hash}")
    print(f"磁力链接: magnet:?xt=urn:btih:{info_hash}")

def format_size(size):
    # 简单的字节转可读格式
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

if __name__ == "__main__":
    # 在这里填入你的 torrent 文件路径
    # parse_torrent("test.torrent")
    
    # 扫描当前目录下所有 torrent
    for fname in os.listdir("."):
        if fname.lower().endswith(".torrent"):
            parse_torrent(fname)
            print("\n")