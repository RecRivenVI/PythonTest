import os
import hashlib
import bencodepy

# 确保 bencodepy 已安装: pip install bencodepy

def calculate_info_hash(file_path):
    """
    计算并返回种子文件的 Info Hash (SHA1)
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            metadata = bencodepy.decode(raw_data)
            
        info_dict = metadata.get(b'info')
        if not info_dict:
            return None
            
        info_encoded = bencodepy.encode(info_dict)
        return hashlib.sha1(info_encoded).hexdigest().upper()
        
    except Exception:
        # 遇到无法解析的文件直接返回 None，不打印错误信息，保持控制台整洁
        return None

def print_magnet_links():
    """
    读取当前目录下所有 .torrent 文件，并逐行打印磁力链接。
    """
    # 查找所有 .torrent 文件
    files = [f for f in os.listdir(".") if f.lower().endswith(".torrent")]
    
    for filename in files:
        info_hash = calculate_info_hash(filename)
        
        if info_hash:
            # 标准磁力链接格式: magnet:?xt=urn:btih:{InfoHash}
            magnet_link = f"magnet:?xt=urn:btih:{info_hash}"
            # 仅打印链接本身，不带任何额外字符或换行符
            print(magnet_link)

if __name__ == "__main__":
    print_magnet_links()