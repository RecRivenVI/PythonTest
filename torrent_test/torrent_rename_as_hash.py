import os
import hashlib
import bencodepy

def calculate_info_hash(file_path):
    """
    计算种子文件的 Info Hash (SHA1)
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            # 解码 Bencode 数据
            metadata = bencodepy.decode(raw_data)
            
        # 获取 info 字典 (key 是 bytes 类型的 b'info')
        info_dict = metadata.get(b'info')
        
        if not info_dict:
            return None

        # 关键步骤：必须对 info 字典重新进行 Bencode 编码，然后计算 SHA1
        info_encoded = bencodepy.encode(info_dict)
        info_hash = hashlib.sha1(info_encoded).hexdigest().upper()
        
        return info_hash
        
    except Exception as e:
        print(f"❌ 解析错误 {file_path}: {e}")
        return None

def rename_files_to_hash():
    print("--- 开始将种子重命名为 Hash 值 ---")
    
    # 获取当前目录下所有 .torrent 文件
    files = [f for f in os.listdir(".") if f.lower().endswith(".torrent")]
    
    if not files:
        print("当前目录下没有找到 .torrent 文件。")
        return

    count_success = 0
    count_skip = 0

    for current_filename in files:
        # 计算哈希
        info_hash = calculate_info_hash(current_filename)
        
        if not info_hash:
            print(f"⚠️  跳过 (无法计算哈希): {current_filename}")
            count_skip += 1
            continue

        # 构建新文件名
        new_filename = f"{info_hash}.torrent"
        
        # 检查是否需要重命名
        if current_filename == new_filename:
            print(f"⏭️  无需重命名 (已是哈希名): {current_filename}")
            count_skip += 1
            continue
            
        # 检查目标文件是否已存在
        # 如果存在，说明你可能有两个不同的文件名，但内容完全一样的种子
        if os.path.exists(new_filename):
            print(f"⚠️  目标已存在 (可能是重复种子): {current_filename} -> {new_filename}")
            # 这里你可以选择是否删除旧文件，目前为了安全选择跳过
            count_skip += 1
            continue

        # 执行重命名
        try:
            os.rename(current_filename, new_filename)
            print(f"✅ 重命名: {current_filename} -> {new_filename}")
            count_success += 1
        except OSError as e:
            print(f"❌ 重命名失败 {current_filename}: {e}")

    print("-" * 30)
    print(f"处理完成。成功: {count_success}, 跳过: {count_skip}")

if __name__ == "__main__":
    rename_files_to_hash()