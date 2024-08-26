import hashlib
import requests
import os
import threading
from typing import Optional, Dict, Any
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

API_KEY = "$2a$10$sgViHwKV/3HN2pY27lBdDOf6wXBXEblI4o4wYYiQQXeZV9G00Yn5S"
API_URL = "https://api.curseforge.com/v1/fingerprints/432"

def calculate_murmurhash2(data: bytes, seed: int = 1) -> int:
    m = 0x5bd1e995
    r = 24
    length = len(data)
    h = seed ^ length
    length4 = length // 4

    for i in range(length4):
        k = int.from_bytes(data[i * 4: (i + 1) * 4], byteorder='little')
        k = (k * m) & 0xFFFFFFFF
        k ^= k >> r
        k = (k * m) & 0xFFFFFFFF
        h = (h * m) & 0xFFFFFFFF
        h ^= k

    extra_bytes = length % 4
    if extra_bytes == 3:
        h ^= data[-3] << 16
        h ^= data[-2] << 8
        h ^= data[-1]
        h = (h * m) & 0xFFFFFFFF
    elif extra_bytes == 2:
        h ^= data[-2] << 8
        h ^= data[-1]
        h = (h * m) & 0xFFFFFFFF
    elif extra_bytes == 1:
        h ^= data[-1]
        h = (h * m) & 0xFFFFFFFF

    h ^= h >> 13
    h = (h * m) & 0xFFFFFFFF
    h ^= h >> 15

    return h

def read_file_and_calculate_hash(file_path: str) -> int:
    with open(file_path, 'rb') as file:
        data = file.read()
    data = bytes([b for b in data if b not in (0x9, 0xa, 0xd, 0x20)])
    return calculate_murmurhash2(data)

def get_remote_mod_info_by_hash(file_hash: int) -> Optional[int]:
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "fingerprints": [file_hash]
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("data") and result["data"].get("exactMatches"):
            return result["data"]["exactMatches"][0]["file"]["modId"]
    return None

def process_mod_files(directory: str, output_text: scrolledtext.ScrolledText):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                file_path = os.path.join(root, file)
                output_text.insert(tk.END, f"Processing file: {file_path}\n")
                file_hash = read_file_and_calculate_hash(file_path)
                mod_id = get_remote_mod_info_by_hash(file_hash)
                if mod_id:
                    output_text.insert(tk.END, f"Mod ID for {file}: {mod_id}\n")
                else:
                    output_text.insert(tk.END, f"No matching mod found for {file}\n")
                output_text.yview(tk.END)

def select_directory(output_text: scrolledtext.ScrolledText):
    directory = filedialog.askdirectory()
    if directory:
        output_text.delete(1.0, tk.END)
        threading.Thread(target=process_mod_files, args=(directory, output_text)).start()

app = tk.Tk()
app.title("CurseForge Mod ID Finder")

frame = tk.Frame(app)
frame.pack(padx=10, pady=10)

select_button = tk.Button(frame, text="Select Directory", command=lambda: select_directory(output_text))
select_button.pack()

output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=80, height=20)
output_text.pack(padx=10, pady=10)

app.mainloop()
