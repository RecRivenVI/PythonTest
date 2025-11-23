import os
import re
import bencodepy
from datetime import datetime, timezone

# 定义非法字符的正则表达式 (针对 Windows/Linux 文件名)
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'

def sanitize_filename(name):
    """
    清洗文件名：将非法字符替换为下划线，并去除首尾空格
    """
    return re.sub(INVALID_CHARS_PATTERN, '_', name).strip()

def rename_torrent_by_metadata(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            metadata = bencodepy.decode(raw_data)
    except Exception as e:
        print(f"❌ 无法读取 {file_path}: {e}")
        return

    info = metadata.get(b'info', {})
    
    # 1. 获取内部名称
    raw_name = info.get(b'name')
    if not raw_name:
        print(f"⚠️  {file_path} 内部没有名称字段，跳过。")
        return
    
    # 解码名称 (处理可能的乱码)
    internal_name = raw_name.decode('utf-8', errors='ignore')
    
    # 2. 获取创建时间
    creation_timestamp = metadata.get(b'creation date')
    if not creation_timestamp:
        print(f"⚠️  {file_path} 内部没有创建时间，跳过。")
        return

    # 格式化时间字符串，例如: 2025-11-20
    # 你可以修改 strftime 中的格式，比如 '%Y%m%d_%H%M'
    dt = datetime.fromtimestamp(creation_timestamp, tz=timezone.utc).astimezone()
    date_str = dt.strftime('%Y-%m-%d')

    # 3. 构建新文件名
    # 格式: 内部名称 + [时间].torrent
    # 清洗名称中的非法字符
    safe_name = sanitize_filename(internal_name)
    
    # 组合新文件名 (你可以根据喜好调整中间的连接符)
    new_filename = f"{safe_name} [{date_str}].torrent"
    
    # 获取文件所在的目录路径
    dir_name = os.path.dirname(file_path)
    new_full_path = os.path.join(dir_name, new_filename)

    # 4. 执行重命名
    if file_path == new_full_path:
        print(f"⏭️  无需重命名: {new_filename}")
        return

    if os.path.exists(new_full_path):
        print(f"⚠️  目标文件已存在，跳过: {new_filename}")
        return

    try:
        os.rename(file_path, new_full_path)
        print(f"✅ 重命名成功:\n   原名: {os.path.basename(file_path)}\n   新名: {new_filename}")
    except OSError as e:
        print(f"❌ 重命名失败: {e}")

if __name__ == "__main__":
    print("--- 开始扫描并重命名 Torrent 文件 ---\n")
    
    # 获取当前目录下的所有文件
    files = [f for f in os.listdir(".") if f.lower().endswith(".torrent")]
    
    if not files:
        print("当前目录下没有找到 .torrent 文件。")
    else:
        for fname in files:
            rename_torrent_by_metadata(fname)
            
    print("\n--- 处理完成 ---")