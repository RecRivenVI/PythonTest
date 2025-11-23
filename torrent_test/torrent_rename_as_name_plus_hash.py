import os
import re
import hashlib
import bencodepy

# 定义非法字符正则（Windows/Linux 文件名不支持的字符）
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'

def sanitize_filename(name):
    """
    清洗文件名：替换非法字符，去除首尾空格
    """
    # 将非法字符替换为下划线，或者你可以改成空格
    return re.sub(INVALID_CHARS_PATTERN, '_', name).strip()

def get_torrent_metadata(file_path):
    """
    读取并返回 (内部名称, InfoHash)
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            metadata = bencodepy.decode(raw_data)
            
        info_dict = metadata.get(b'info')
        if not info_dict:
            return None, None

        # 1. 计算 Hash
        # 必须对 info 字典的原始 bencode 字节流进行 hash
        info_encoded = bencodepy.encode(info_dict)
        info_hash = hashlib.sha1(info_encoded).hexdigest().upper()

        # 2. 获取内部名称
        # 优先使用 info['name']，这是种子内容的根目录名或文件名
        raw_name = info_dict.get(b'name', b'Unknown')
        # 解码并处理乱码
        internal_name = raw_name.decode('utf-8', errors='ignore')

        return internal_name, info_hash

    except Exception as e:
        print(f"❌ 解析出错 {file_path}: {e}")
        return None, None

def rename_torrents_name_plus_hash():
    print("--- 开始重命名: 名称 + [Hash] ---")
    
    files = [f for f in os.listdir(".") if f.lower().endswith(".torrent")]
    
    if not files:
        print("当前目录下没有找到 .torrent 文件。")
        return

    count_success = 0
    count_skip = 0

    for current_filename in files:
        # 获取元数据
        name, info_hash = get_torrent_metadata(current_filename)
        
        if not name or not info_hash:
            print(f"⚠️  跳过 (数据不完整): {current_filename}")
            count_skip += 1
            continue

        # 清洗名称，防止含有 / \ : * ? " < > |
        safe_name = sanitize_filename(name)

        # --- 构建新文件名 ---
        # 格式示例: Adobe Photoshop [55BC19...].torrent
        # 你可以根据喜好修改这里的格式
        new_filename = f"{safe_name} [{info_hash}].torrent"
        
        # 检查是否需要重命名
        if current_filename == new_filename:
            print(f"⏭️  无需修改: {current_filename}")
            count_skip += 1
            continue

        # 检查目标是否存在
        if os.path.exists(new_filename):
            print(f"⚠️  目标已存在，跳过: {new_filename}")
            count_skip += 1
            continue

        # 执行重命名
        try:
            os.rename(current_filename, new_filename)
            print(f"✅ 重命名:\n   旧: {current_filename}\n   新: {new_filename}")
            count_success += 1
        except OSError as e:
            print(f"❌ 系统错误: {e}")

    print("-" * 30)
    print(f"处理完成。成功: {count_success}, 跳过: {count_skip}")

if __name__ == "__main__":
    rename_torrents_name_plus_hash()