import hashlib

def generate_file_fingerprint_sha1(file_path):
    """Generate a fingerprint for a file using SHA-1 and return the hex digest and integer value."""
    hash_func = hashlib.sha1()
    
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
    except IOError as e:
        print(f"Error reading file: {e}")
        return None, None
    
    # 获取 SHA-1 哈希值的十六进制字符串
    hex_digest = hash_func.hexdigest()
    
    # 将十六进制字符串转换为整数
    int_value = int(hex_digest, 16)
    
    return hex_digest, int_value

# 示例用法
file_path = r"F:\PythonTestbench\jars\jei-1.20.1-forge-15.8.2.23.jar"
fingerprint, int_fingerprint = generate_file_fingerprint_sha1(file_path)
if fingerprint:
    print(f'File fingerprint (SHA-1): {fingerprint}')
    print(f'Fingerprint as integer: {int_fingerprint}')
else:
    print('Failed to generate fingerprint.')
