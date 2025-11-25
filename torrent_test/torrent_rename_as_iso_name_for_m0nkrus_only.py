import os
import re
import hashlib
import bencodepy

# 定义非法字符的正则表达式
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'

def sanitize_filename(name):
    """
    清洗文件名：将非法字符替换为下划线，并去除首尾空格
    """
    return re.sub(INVALID_CHARS_PATTERN, '_', name).strip()

def get_iso_name_and_hash(torrent_path):
    """
    解析 Torrent 文件，返回 (ISO文件名, InfoHash) 或 (None, None, 原因)
    """
    try:
        with open(torrent_path, 'rb') as f:
            metadata = bencodepy.decode(f.read())
            
        info_dict = metadata.get(b'info')
        if not info_dict:
            return None, None, "缺少 'info' 字段"
            
    except Exception:
        return None, None, "文件解析失败或已损坏"

    # --- 1. 计算 Info Hash (在解析 ISO 前进行，如果结构损坏则提前退出) ---
    try:
        info_encoded = bencodepy.encode(info_dict)
        info_hash = hashlib.sha1(info_encoded).hexdigest().upper()
    except Exception:
        return None, None, "计算哈希失败"

    all_iso_paths = []
    
    # 获取文件列表 (处理单文件和多文件模式)
    file_list = info_dict.get(b'files')
    
    if file_list:
        # 多文件模式
        for file_entry in file_list:
            path_components = file_entry.get(b'path', [])
            if path_components and path_components[-1].lower().endswith(b'.iso'):
                # 拼接路径 (例如: Folder/My.iso)
                full_iso_path = os.path.join(*[p.decode('utf-8', errors='ignore') for p in path_components])
                all_iso_paths.append(full_iso_path)
    
    elif b'length' in info_dict and b'name' in info_dict:
        # 单文件模式 (文件名即为 info['name'])
        filename = info_dict[b'name'].decode('utf-8', errors='ignore')
        if filename.lower().endswith('.iso'):
            all_iso_paths.append(filename)

    # --- 2. 验证 ISO 数量 ---
    num_isos = len(all_iso_paths)
    
    if num_isos == 1:
        # 成功：获取 ISO 文件的基础文件名
        # 使用 os.path.basename 确保只获取文件名部分，不包含路径
        iso_basename = os.path.basename(all_iso_paths[0])
        return iso_basename, info_hash, None # 成功返回 (ISO文件名, Hash, None)
        
    elif num_isos == 0:
        return None, None, "未找到任何 .iso 文件"
    else: # num_isos > 1
        return None, None, f"找到 {num_isos} 个 .iso 文件"


def rename_to_iso_hash():
    print("--- 开始重命名: {ISO文件名} + [HASH] ---")
    
    files = [f for f in os.listdir(".") if f.lower().endswith(".torrent")]
    
    if not files:
        print("当前目录下没有找到 .torrent 文件。")
        return

    count_success = 0

    for current_filename in files:
        iso_name, info_hash, reason = get_iso_name_and_hash(current_filename)
        
        print("-" * 50)
        print(f"处理文件: {current_filename}")

        if not iso_name:
            print(f"⚠️  跳过。原因: {reason}")
            continue

        # 清洗 ISO 文件名 (以防文件名中含有非法字符)
        safe_iso_name = sanitize_filename(iso_name)
        
        # --- 构建新文件名 ---
        # 格式: ISO文件名 [HASH].torrent
        new_filename = f"{safe_iso_name} [{info_hash}].torrent"
        
        # 检查是否需要重命名
        if current_filename == new_filename:
            print(f"⏭️  无需修改 (文件名已是目标格式)")
            continue

        # 检查目标是否存在
        if os.path.exists(new_filename):
            print(f"⚠️  目标已存在 ({new_filename})，跳过，请手动检查重复项。")
            continue

        # 执行重命名
        try:
            os.rename(current_filename, new_filename)
            print(f"✅ 重命名成功:\n   新名: {new_filename}")
            count_success += 1
        except OSError as e:
            print(f"❌ 系统错误，重命名失败: {e}")

    print("-" * 50)
    print(f"处理完成。成功重命名 {count_success} 个文件。")

if __name__ == "__main__":
    rename_to_iso_hash()