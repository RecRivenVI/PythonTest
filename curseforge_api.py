import os
import json
import requests
import zipfile
import toml
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 设置 API 密钥
API_KEY = '$2a$10$sgViHwKV/3HN2pY27lBdDOf6wXBXEblI4o4wYYiQQXeZV9G00Yn5S'
BASE_URL = 'https://api.curseforge.com/v1'

# 本地模组文件夹路径
local_mods_path = 'F:/PythonTestbench/jars1'

def get_mod_info_from_curseforge(mod_id):
    headers = {
        'x-api-key': API_KEY
    }
    url = f'{BASE_URL}/mods/{mod_id}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        logging.error(f'访问被拒绝，模组 ID {mod_id}，状态码 {response.status_code}')
    elif response.status_code == 404:
        logging.error(f'模组 ID {mod_id} 未找到')
    else:
        logging.error(f'获取模组信息失败，模组 ID {mod_id}，状态码 {response.status_code}')
    
    return None

def extract_mod_id_and_version(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # 检查文件是否存在
            if 'META-INF/mods.toml' in jar.namelist():
                with jar.open('META-INF/mods.toml') as mod_file:
                    mod_data = toml.loads(mod_file.read().decode('utf-8'))
                    mod_id = mod_data['mods'][0]['modId']
                    version = mod_data['mods'][0]['version']
                    return mod_id, version
            else:
                logging.warning(f'{jar_path} 中没有 META-INF/mods.toml 文件')
    except (FileNotFoundError, zipfile.BadZipFile, KeyError, toml.TomlDecodeError) as e:
        logging.error(f'读取 {jar_path} 时出错：{e}')
    
    return None, None

def scan_local_mods():
    mod_infos = []

    for mod_file in os.listdir(local_mods_path):
        if mod_file.endswith('.jar'):
            jar_path = os.path.join(local_mods_path, mod_file)
            mod_id, version = extract_mod_id_and_version(jar_path)
            if mod_id:
                mod_info = get_mod_info_from_curseforge(mod_id)
                if mod_info:
                    mod_info['data']['version'] = version
                    mod_infos.append(mod_info)
                else:
                    logging.warning(f'模组 ID {mod_id} 没有返回信息')
            else:
                logging.warning(f'在 {jar_path} 中未找到模组 ID')
    
    return mod_infos

def main():
    mod_infos = scan_local_mods()
    if mod_infos:
        with open('local_mod_infos.json', 'w', encoding='gbk') as f:
            json.dump(mod_infos, f, indent=4, ensure_ascii=False)
        logging.info('模组信息已保存到 local_mod_infos.json')
    else:
        logging.info('未找到模组信息')

if __name__ == "__main__":
    main()
