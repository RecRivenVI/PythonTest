import os
from PIL import Image

# 常见图片文件头（魔数）
MAGIC_NUMBERS = {
    b"\x89PNG\r\n\x1a\n": "png",   # PNG
    b"\xff\xd8\xff": "jpg",        # JPEG
    b"GIF87a": "gif",              # GIF (87a)
    b"GIF89a": "gif",              # GIF (89a)
    b"RIFF": "webp",               # WEBP (RIFF....WEBP)
    b"BM": "bmp",                  # BMP
}

def detect_format(file_path):
    """根据文件头检测图片格式"""
    with open(file_path, "rb") as f:
        header = f.read(12)  # 读取前12字节足够判断常见格式
    for magic, fmt in MAGIC_NUMBERS.items():
        if header.startswith(magic):
            # 特殊处理 WEBP: RIFF 开头且第8-12字节是 'WEBP'
            if fmt == "webp" and header[8:12] != b"WEBP":
                continue
            return fmt
    return None

def convert_to_png():
    """检测目录下所有文件，如果是图片则转换为 PNG"""
    for filename in os.listdir("."):
        if not os.path.isfile(filename):
            continue
        real_fmt = detect_format(filename)
        if real_fmt:
            base, _ = os.path.splitext(filename)
            new_name = f"{base}.png"
            try:
                with Image.open(filename) as img:
                    img.convert("RGBA").save(new_name, "PNG")
                print(f"[转换成功] {filename} ({real_fmt}) -> {new_name}")
            except Exception as e:
                print(f"[失败] {filename}: {e}")
        else:
            print(f"[跳过] {filename} 非图片文件")

if __name__ == "__main__":
    convert_to_png()
