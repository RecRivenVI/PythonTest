import xml.etree.ElementTree as ET

def is_mv_photo(file_path):
    try:
        print(f"Processing file: {file_path}")
        
        with open(file_path, 'rb') as f:
            data = f.read()

            # 查找 XMP 数据的位置
            start = data.find(b'<x:xmpmeta')
            end = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
            
            print(f"Start of XMP data: {start}, End of XMP data: {end}")

            if start == -1 or end == -1:
                print("No XMP data found.")
                return False
            
            # 提取 XMP 数据并解码
            xmp_data = data[start:end]
            xmp_string = xmp_data.decode('utf-8', errors='ignore')
            
            # 打印提取的 XMP 数据
            print(f"Extracted XMP data:\n{xmp_string}\n")

            # 解析 XML
            root = ET.fromstring(xmp_string)
            print("Parsed XML successfully.")

            # 查找 rdf:Description 标签
            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'x': 'adobe:ns:meta/',
                'GCamera': 'http://ns.google.com/photos/1.0/camera/',
                'MiCamera': 'http://ns.xiaomi.com/photos/1.0/camera/'
            }

            description = root.find('.//rdf:Description', ns)

            # 检查是否找到了 rdf:Description
            if description is not None:
                print("Found rdf:Description.")
                
                # 尝试从不同的命名空间获取 GCamera:MicroVideo 属性
                micro_video = description.get('{http://ns.google.com/photos/1.0/camera/}MicroVideo')
                print(f"GCamera:MicroVideo value: {micro_video}")
                
                # 检查 MicroVideo 属性的值
                if micro_video == "1":
                    print(f"{file_path} is a MVIMG (Micro Video) photo.")
                    return True
            else:
                print("Did not find rdf:Description.")

            print(f"{file_path} is a regular photo.")
            return False

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

# 测试文件路径
file_path = r"F:\照片整理目录\自己照片\分类\Xiaomi\23116PN5BC\Photo\MVIMG_20231218_081249.jpg"
is_mv_photo(file_path)
