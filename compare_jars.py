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

def get_mods_from_jar(jar_file_path):
    mods_toml = read_mods_toml(jar_file_path)
    if mods_toml is not None:
        # 返回 mods 表格
        return mods_toml.get('mods', [])
    return []

def process_jars(directory):
    mods_info = {}
    for filename in os.listdir(directory):
        if filename.endswith('.jar'):
            full_path = os.path.join(directory, filename)
            mods = get_mods_from_jar(full_path)
            if mods:
                mods_info[filename] = mods
    return mods_info

def compare_mods(mods_info1, mods_info2):
    common_mods = set(mods_info1.keys()) & set(mods_info2.keys())
    unique_to_dir1 = set(mods_info1.keys()) - set(mods_info2.keys())
    unique_to_dir2 = set(mods_info2.keys()) - set(mods_info1.keys())

    # 输出共同的 .jar 文件中的 modId 和 version
    print("Common mods:")
    for jar in common_mods:
        mods1 = mods_info1[jar]
        mods2 = mods_info2[jar]
        for i in range(min(len(mods1), len(mods2))):
            mod1 = mods1[i]
            mod2 = mods2[i]
            if mod1 == mod2:
                print(f"{jar}: {mod1['modId']} (same)")
            else:
                print(f"{jar}: {mod1['modId']} (different)")

    # 输出仅存在于第一个目录中的 .jar 文件
    print("\nUnique to first directory:")
    for jar in unique_to_dir1:
        print(jar)

    # 输出仅存在于第二个目录中的 .jar 文件
    print("\nUnique to second directory:")
    for jar in unique_to_dir2:
        print(jar)

directory1 = r"F:\PythonTestbench\jars1"
directory2 = r"F:\PythonTestbench\jars2"

mods_info1 = process_jars(directory1)
mods_info2 = process_jars(directory2)

compare_mods(mods_info1, mods_info2)