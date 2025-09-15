#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# 小米 OTA 接口地址
MIUI_UPDATE_URL = "https://update.miui.com/updates/miotaV3.php"
AES_IV = b"0102030405060708"
DEFAULT_KEY = b"miuiotavalided11"  # v1 接口密钥，无需登录

def build_payload(device, version, android, user_id="0"):
    payload = {
        "id": user_id,
        "c": android,
        "d": device,
        "f": "1",
        "ov": version,
        "l": "zh_CN" if "_global" not in device else "en_US",
        "r": "CN" if "_global" not in device else "GL",
        "v": f"miui-{version.replace('OS1', 'V816')}"
    }
    return json.dumps(payload, separators=(",", ":"))

def encrypt_payload(payload, key):
    cipher = AES.new(key, AES.MODE_CBC, AES_IV)
    padded = pad(payload.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_response(encrypted_text, key):
    cipher = AES.new(key, AES.MODE_CBC, AES_IV)
    decoded = base64.urlsafe_b64decode(encrypted_text)
    decrypted = unpad(cipher.decrypt(decoded), AES.block_size)
    return json.loads(decrypted.decode())

def query_update(device, version, android, user_id="0", key=DEFAULT_KEY, service_token=""):
    interface = "2" if service_token else "1"
    payload = build_payload(device, version, android, user_id)
    encrypted_payload = encrypt_payload(payload, key)

    post_data = {
        "q": encrypted_payload,
        "t": service_token,
        "s": interface
    }

    try:
        response = requests.post(MIUI_UPDATE_URL, data=post_data)
        response.raise_for_status()
        return decrypt_response(response.text, key)
    except Exception as e:
        print("请求失败:", e)
        return None

def print_result(result):
    if not result or "CurrentRom" not in result:
        print("未获取到 ROM 信息，原始返回内容如下：\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    rom = result["CurrentRom"]
    print(f"\n设备: {rom.get('device', 'N/A')}")
    print(f"版本: {rom.get('version', 'N/A')}")
    print(f"Android: {rom.get('codebase', 'N/A')}")
    print(f"分支: {rom.get('branch', 'N/A')}")
    print(f"文件名: {rom.get('filename', 'N/A')}")
    print(f"大小: {rom.get('filesize', 'N/A')}")
    print(f"下载链接: https://bigota.d.miui.com/{rom.get('version')}/{rom.get('filename')}")
    changelog = rom.get('changelog', '')
    if changelog:
        print("\n更新日志:\n", changelog)


if __name__ == "__main__":
    # 示例：小米 13（fuxi） + Android 14 + HyperOS 版本号
    device = input("设备代号（如 fuxi）: ")
    version = input("系统版本（如 OS1.0.9.0.UNCCNXM）: ")
    android = input("Android版本（如 14）: ")

    rom_info = query_update(device, version, android)
    print_result(rom_info)
