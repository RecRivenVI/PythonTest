import os

# 定义常见图片文件头（魔数）
MAGIC_NUMBERS = {
    b"\x89PNG\r\n\x1a\n": "png",   # PNG 文件头
    b"\xff\xd8\xff": "jpg",        # JPEG 文件头
}

def detect_format(file_path):
    """根据文件头检测图片格式"""
    with open(file_path, "rb") as f:
        header = f.read(8)  # 读取前8字节足够判断PNG/JPEG
    for magic, fmt in MAGIC_NUMBERS.items():
        if header.startswith(magic):
            return fmt
    return None

def fix_extensions():
    """检测并修复当前目录下的图片扩展名"""
    for filename in os.listdir("."):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            real_fmt = detect_format(filename)
            if real_fmt:
                base, _ = os.path.splitext(filename)
                correct_name = f"{base}.{real_fmt}"
                if filename.lower() != correct_name.lower():
                    print(f"[修复] {filename} -> {correct_name}")
                    os.rename(filename, correct_name)
                else:
                    print(f"[正确] {filename} 已匹配格式 {real_fmt}")
            else:
                print(f"[跳过] {filename} 未识别文件头")

if __name__ == "__main__":
    fix_extensions()
