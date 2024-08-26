import os
import zipfile
import toml

def read_mods_toml(jar_file_path):
    try:
        import toml
    except ImportError:
        print("The 'toml' module is required but not installed.")
        print("Please install it using: pip install toml")
        return None
    
    # 尝试打开 jar 文件
    with zipfile.ZipFile(jar_file_path, 'r') as jar:
        # 检查 mods.toml 是否存在于 META-INF 目录下
        if 'META-INF/mods.toml' in jar.namelist():
            # 读取 mods.toml 文件
            toml_data = jar.read('META-INF/mods.toml')
            # 解码字节串为字符串
            toml_str = toml_data.decode('utf-8')
            return toml.loads(toml_str)
        else:
            print(f"No META-INF/mods.toml found in {jar_file_path}")
            return None

def process_jar(jar_file_path):
    mods_toml = read_mods_toml(jar_file_path)
    if mods_toml is not None:
        # 直接访问 [[mods]] 表格
        mods = mods_toml.get('mods', [])
        if isinstance(mods, list) and len(mods) > 0:
            mod = mods[0]
            mod_id = mod.get('modId')
            version = mod.get('version')
            if mod_id and version:
                print(f"modId: {mod_id}, version: {version}")
        else:
            print(f"No valid [[mods]] table found in {jar_file_path}")

def process_jars(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jar'):
            full_path = os.path.join(directory, filename)
            process_jar(full_path)

process_jars(r"F:\PythonTestbench")