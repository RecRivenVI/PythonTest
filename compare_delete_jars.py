import os
import zipfile
import toml
import hashlib
from packaging.version import parse, InvalidVersion
import logging
import re

# 设置日志配置
logging.basicConfig(filename='mod_processor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_version(version):
    """Normalizes common non-standard version formats."""
    if not version:
        return '0.0.0'
    
    # 删除非数字和非字母字符
    normalized_version = re.sub(r'[^0-9a-zA-Z\.]', '', version)
    
    # 处理一些常见的非标准版本格式
    if re.match(r'^\d+\.\d+\.\d+$', normalized_version):
        return normalized_version
    elif re.match(r'^\d+\.\d+$', normalized_version):
        return normalized_version + '.0'
    elif re.match(r'^\d+$', normalized_version):
        return normalized_version + '.0.0'
    else:
        return '0.0.0'

def read_mods_toml(jar_file_path):
    """Reads the mods.toml file from a given JAR file."""
    try:
        with zipfile.ZipFile(jar_file_path, 'r') as jar:
            if 'META-INF/mods.toml' in jar.namelist():
                toml_data = jar.read('META-INF/mods.toml')
                toml_str = toml_data.decode('utf-8')
                return toml.loads(toml_str)
            else:
                logging.warning(f"No mods.toml found in {jar_file_path}")
                print(f"No mods.toml found in {jar_file_path}")
    except Exception as e:
        logging.error(f"Error reading {jar_file_path}: {e}")
        print(f"Error reading {jar_file_path}: {e}")
    return None

def read_manifest_version(jar_file_path):
    """Reads the Implementation-Version from the MANIFEST.MF file in a given JAR file."""
    try:
        with zipfile.ZipFile(jar_file_path, 'r') as jar:
            if 'META-INF/MANIFEST.MF' in jar.namelist():
                manifest_data = jar.read('META-INF/MANIFEST.MF').decode('utf-8')
                for line in manifest_data.splitlines():
                    if line.startswith('Implementation-Version:'):
                        return line.split(':', 1)[1].strip()
            else:
                logging.warning(f"No MANIFEST.MF found in {jar_file_path}")
                print(f"No MANIFEST.MF found in {jar_file_path}")
    except Exception as e:
        logging.error(f"Error reading MANIFEST.MF from {jar_file_path}: {e}")
        print(f"Error reading MANIFEST.MF from {jar_file_path}: {e}")
    return None

def get_mods_from_jar(jar_file_path):
    """Extracts mod information from a JAR file."""
    mods_toml = read_mods_toml(jar_file_path)
    mods = []
    if mods_toml and 'mods' in mods_toml and len(mods_toml['mods']) > 0:
        for mod in mods_toml['mods']:
            if 'modId' in mod:
                mod_id = mod['modId']
                version = mod.get('version', '0.0.0')
                if version == "${file.jarVersion}":
                    version = read_manifest_version(jar_file_path)
                    if version is None:
                        logging.warning(f"No Implementation-Version found in MANIFEST.MF for {jar_file_path}, using '0.0.0'")
                        print(f"No Implementation-Version found in MANIFEST.MF for {jar_file_path}, using '0.0.0'")
                        version = '0.0.0'
                normalized_version = normalize_version(version)
                if not is_valid_version(normalized_version):
                    logging.warning(f"Invalid version '{version}' for mod '{mod_id}' in {jar_file_path}, using '0.0.0'")
                    print(f"Invalid version '{version}' for mod '{mod_id}' in {jar_file_path}, using '0.0.0'")
                    normalized_version = '0.0.0'
                mods.append({'modId': mod_id, 'version': normalized_version})
    else:
        logging.warning(f"No valid mods found in {jar_file_path}. Attempting to read MANIFEST.MF.")
        print(f"No valid mods found in {jar_file_path}. Attempting to read MANIFEST.MF.")
        version = read_manifest_version(jar_file_path)
        if version is None:
            logging.warning(f"No version information found in {jar_file_path}, using '0.0.0'")
            print(f"No version information found in {jar_file_path}, using '0.0.0'")
            version = '0.0.0'
        mod_id = os.path.basename(jar_file_path).replace('.jar', '')
        normalized_version = normalize_version(version)
        if not is_valid_version(normalized_version):
            logging.warning(f"Invalid version '{version}' for mod '{mod_id}' in {jar_file_path}, using '0.0.0'")
            print(f"Invalid version '{version}' for mod '{mod_id}' in {jar_file_path}, using '0.0.0'")
            normalized_version = '0.0.0'
        mods.append({'modId': mod_id, 'version': normalized_version})

    return mods

def calculate_sha1(file_path):
    """Calculates the SHA-1 hash of a file."""
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # Read in chunks of 64KB
                if not data:
                    break
                sha1.update(data)
    except Exception as e:
        logging.error(f"Error calculating SHA-1 for {file_path}: {e}")
        print(f"Error calculating SHA-1 for {file_path}: {e}")
    return sha1.hexdigest()

def process_jars(directory, missing_toml_file):
    """Processes all JAR files in a directory to extract mod information and calculate SHA-1 hashes."""
    if not os.path.exists(directory):
        logging.error(f"Directory does not exist: {directory}")
        print(f"Directory does not exist: {directory}")
        return {}

    mods_info = {}
    missing_toml = []

    for filename in os.listdir(directory):
        if filename.endswith('.jar'):
            full_path = os.path.join(directory, filename)
            mods = get_mods_from_jar(full_path)
            if mods:
                mods_info[filename] = {
                    'mods': mods,
                    'sha1': calculate_sha1(full_path)
                }
            else:
                missing_toml.append(filename)

    if missing_toml:
        with open(missing_toml_file, 'a') as file:
            for jar in missing_toml:
                file.write(jar + '\n')
        logging.info(f"Missing mods.toml files: {missing_toml}")
        print(f"Missing mods.toml files: {missing_toml}")

    return mods_info

def is_valid_version(version):
    """Checks if a version string is valid."""
    try:
        parse(version)
        return True
    except InvalidVersion:
        return False

def compare_versions(version1, version2):
    """Compares two version strings."""
    v1, v2 = parse(version1), parse(version2)
    return (v1 > v2) - (v1 < v2)

def find_duplicates(mods_info):
    """Finds duplicate mods based on version comparison."""
    mod_id_map = {}
    duplicates = []

    for jar, info in mods_info.items():
        for mod in info['mods']:
            mod_id = mod['modId']
            version = mod['version']
            if mod_id in mod_id_map:
                existing_jar, existing_version = mod_id_map[mod_id]
                comparison = compare_versions(existing_version, version)
                if comparison < 0:
                    duplicates.append(existing_jar)
                    mod_id_map[mod_id] = (jar, version)
                elif comparison > 0:
                    duplicates.append(jar)
            else:
                mod_id_map[mod_id] = (jar, version)

    return list(set(duplicates))

def delete_files(directory, files):
    """Deletes specified files from a directory."""
    for file in files:
        full_path = os.path.join(directory, file)
        try:
            os.remove(full_path)
            logging.info(f"Deleted: {full_path}")
            print(f"Deleted: {full_path}")
        except Exception as e:
            logging.error(f"Error deleting {full_path}: {e}")
            print(f"Error deleting {full_path}: {e}")

def main():
    directory = input("Enter the directory containing JAR files: ")
    missing_toml_file = "missing_toml.txt"

    mods_info = process_jars(directory, missing_toml_file)
    if not mods_info:
        return

    duplicates = find_duplicates(mods_info)

    if duplicates:
        print("Found duplicates based on version comparison:")
        for jar in duplicates:
            print(jar)

        user_input = input("Do you want to delete these files? (y/n): ")
        if user_input.lower() == 'y':
            delete_files(directory, duplicates)
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()
