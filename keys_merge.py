def load_config(file_path):
    """读取配置文件并返回字典形式的键位设定"""
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # 忽略空行
                key, value = line.split(':', 1)
                config[key.strip()] = value.strip()  # 去掉键和值的多余空格
    return config

def save_config(file_path, config):
    """将字典形式的键位设定保存到配置文件"""
    with open(file_path, 'w') as file:
        for key, value in config.items():
            file.write(f"{key}:{value}\n")  # 去掉冒号后的多余空格

def merge_configs(base_file_path, override_file_path, output_file_path):
    """将覆盖配置应用到基础配置中"""
    # 读取配置文件
    base_config = load_config(base_file_path)
    override_config = load_config(override_file_path)
    
    # 合并配置
    merged_config = base_config.copy()
    for key in override_config:
        # 只将常用配置中的键覆盖到基础配置中
        if key in base_config:
            merged_config[key] = override_config[key]
        else:
            # 如果大型配置中有而常用配置中没有的键，保留基础配置中的键
            merged_config[key] = base_config.get(key, override_config[key])

    # 保存合并后的配置
    save_config(output_file_path, merged_config)

# 文件路径
base_file_path = 'large_config.txt'  # 更大的设定文件路径
override_file_path = 'habit_config.txt'  # 习惯按键设定文件路径
output_file_path = 'merged_config.txt'  # 合并后的设定文件路径

# 合并配置
merge_configs(base_file_path, override_file_path, output_file_path)

print(f"合并后的设定已保存到 {output_file_path}")
