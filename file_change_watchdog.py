import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

class MoveHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        self.log_file = log_file
        self.moved_files = {}

        # Load previously moved files from log file
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.moved_files = json.load(f)

    def on_moved(self, event):
        if event.is_directory:
            return

        src_path = event.src_path
        dst_path = event.dest_path
        print(f'文件移动: {src_path} 到 {dst_path}')

        # Log the move operation
        self.moved_files[src_path] = {'action': 'moved', 'destination': dst_path}
        self.save_log()

    def on_deleted(self, event):
        if event.is_directory:
            return

        src_path = event.src_path
        print(f'文件删除: {src_path}')

        # Log the delete operation
        self.moved_files[src_path] = {'action': 'deleted'}
        self.save_log()

    def on_modified(self, event):
        if event.is_directory:
            return

        src_path = event.src_path
        print(f'文件修改: {src_path}')

        # Log the rename operation (if the file name has changed)
        if os.path.exists(src_path):
            self.moved_files[src_path] = {'action': 'renamed'}
            self.save_log()

    def save_log(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.moved_files, f, ensure_ascii=False, indent=4)

    def restore_file(self, src_path):
        if src_path in self.moved_files:
            action_info = self.moved_files[src_path]
            if action_info['action'] == 'moved':
                dst_path = action_info['destination']
                # Restore the file to its original location
                shutil.move(dst_path, src_path)
                print(f'恢复: {dst_path} 到 {src_path}')
            elif action_info['action'] == 'deleted':
                print(f'文件已删除: {src_path}，无法恢复。')
            del self.moved_files[src_path]  # Remove from log after restoration
            self.save_log()
        else:
            print(f'未在日志中找到文件: {src_path}')

def monitor_folder(folder_path, log_file):
    event_handler = MoveHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f'开始监控: {folder_path}')

    try:
        while True:
            command = input("输入 'restore <original_path>' 来恢复文件，或输入 'exit' 退出: ")
            if command.startswith('restore '):
                original_path = command.split(' ', 1)[1]
                event_handler.restore_file(original_path)
            elif command == 'exit':
                break
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# 示例用法:
folder_to_monitor = r'F:\照片整理目录\老妈照片'  # 替换为你的文件夹路径
log_file_path = 'moved_files_log.json'  # 用于记录移动文件的日志文件
monitor_folder(folder_to_monitor, log_file_path)
