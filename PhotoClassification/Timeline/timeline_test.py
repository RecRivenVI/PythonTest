import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from datetime import datetime
import os
import mplcursors

# 设置 matplotlib 使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# 数据文件路径
file_path = os.path.join(os.getcwd(), 'timeline_data.csv')

# 创建主窗口
root = tk.Tk()
root.title("时间轴生成器")
root.geometry("800x500")  # 调整窗口默认大小

# 创建表格头部
columns = ('人物', '设备名称', '开始时间', '结束时间')

# 包装 Treeview 用于支持滚动条
tree_frame = tk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True)

# 添加滚动条
scrollbar = tk.Scrollbar(tree_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
scrollbar.config(command=tree.yview)
tree.pack(fill=tk.BOTH, expand=True)

tree.heading('人物', text='人物')
tree.heading('设备名称', text='设备名称')
tree.heading('开始时间', text='开始时间 (YYYY-MM-DD)')
tree.heading('结束时间', text='结束时间 (YYYY-MM-DD)')

# 加载数据
def load_data():
    if os.path.exists(file_path):
        encodings = ['utf-8', 'gbk', 'latin1']  # 尝试的编码列表
        for enc in encodings:
            try:
                with open(file_path, encoding=enc) as f:
                    # 手动逐行读取，检查是否有不一致的列数
                    data = f.readlines()
                    header = data[0].strip().split(',')
                    if len(header) != 4:
                        raise ValueError(f"CSV 文件的列数不正确，期望 4 列，实际 {len(header)} 列")

                    df = pd.read_csv(file_path, encoding=enc)
                    print("成功读取编码:", enc)
                    print("读取的列名:", df.columns.tolist())

                    # 确保列数正确
                    if len(df.columns) != 4:
                        raise ValueError(f"CSV 文件的列数不正确，期望 4 列，实际 {len(df.columns)} 列")

                    df.columns = ['人物', '设备名称', '开始时间', '结束时间']  # 重命名列

                    # 清理数据
                    df = df.dropna()  # 删除任何包含缺失值的行
                    df = df.reset_index(drop=True)  # 重置索引

                    # 确保每一列都被正确地转换为字符串
                    for col in df.columns:
                        df[col] = df[col].astype(str)

                    # 插入数据到 Treeview
                    for _, row in df.iterrows():
                        tree.insert('', tk.END, values=(row['人物'], row['设备名称'], row['开始时间'], row['结束时间']))
                    return  # 成功读取数据后退出函数
            except Exception as e:
                print(f"尝试编码 {enc} 时出现错误: {e}")  # 打印错误信息
        messagebox.showerror("加载错误", "无法读取 CSV 文件，请检查文件格式或编码。")


# 生成时间轴
def plot_timeline():
    try:
        encodings = ['utf-8', 'gbk', 'latin1']  # 尝试的编码列表
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                print("成功读取编码:", enc)  # 打印成功的编码
                print("读取的列名:", df.columns.tolist())  # 打印列名以确认
                df.columns = ['人物', '设备名称', '开始时间', '结束时间']  # 重命名列

                # 清理数据
                df = df.dropna()  # 删除任何包含缺失值的行
                df = df.reset_index(drop=True)  # 重置索引

                # 确保每一列都被正确地转换为字符串
                for col in df.columns:
                    df[col] = df[col].astype(str)

                # 确保日期列为 datetime 类型
                df['开始时间'] = pd.to_datetime(df['开始时间'], format='%Y-%m-%d', errors='coerce')
                df['结束时间'] = pd.to_datetime(df['结束时间'], format='%Y-%m-%d', errors='coerce')

                # 检查是否有缺失值
                invalid_rows = df[df['开始时间'].isnull() | df['结束时间'].isnull()]
                if not invalid_rows.empty:
                    messagebox.showerror("日期错误", f"日期格式错误或存在缺失值，请检查以下行: {invalid_rows.index.tolist()}")
                    return

                # 创建绘图
                fig, ax = plt.subplots(figsize=(10, 6))

                # 设置Y轴的刻度
                y_labels = df['人物'] + ' - ' + df['设备名称']
                ax.set_yticks(range(len(df)))
                ax.set_yticklabels(y_labels)

                # 将时间数据转换为 Matplotlib 支持的日期格式
                start_dates = date2num(df['开始时间'])
                end_dates = date2num(df['结束时间'])
                durations = end_dates - start_dates

                # 绘制 broken_barh 图
                ax.broken_barh(list(zip(start_dates, durations)), [(i - 0.4, 0.8) for i in range(len(df))], facecolors='tab:blue')

                # 设置X轴格式为日期
                ax.xaxis_date()

                # 添加标题和网格
                ax.set_title("时间轴")
                ax.grid(True)

                # 使用 mplcursors 实现悬停显示开始和结束时间
                cursor = mplcursors.cursor(hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    index = sel.index
                    start_time = df.iloc[index]['开始时间'].strftime('%Y-%m-%d')
                    end_time = df.iloc[index]['结束时间'].strftime('%Y-%m-%d')
                    sel.annotation.set(text=f"开始: {start_time}\n结束: {end_time}")

                # 显示图形
                plt.show()
                return  # 成功读取数据后退出函数

            except Exception as e:
                print(f"尝试编码 {enc} 时出现错误: {e}")  # 打印错误信息

        messagebox.showerror("加载错误", "无法读取 CSV 文件，请检查编码和文件内容。")

    except Exception as e:
        messagebox.showerror("绘图错误", f"无法生成时间轴: {e}")

# 保存数据
def save_data():
    data = []
    for item in tree.get_children():
        data.append(tree.item(item)['values'])
    
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(file_path, index=False, encoding='utf-8')
    messagebox.showinfo("保存成功", "数据已保存到 CSV 文件。")

# 按钮框架
button_frame = tk.Frame(root)
button_frame.pack()

# 生成时间轴按钮
plot_button = tk.Button(button_frame, text="生成时间轴", command=plot_timeline)
plot_button.pack(side=tk.LEFT, padx=5, pady=5)

# 保存数据按钮
save_button = tk.Button(button_frame, text="保存数据", command=save_data)
save_button.pack(side=tk.LEFT, padx=5, pady=5)

# 添加新的数据条目
def add_entry():
    def add_data():
        person = person_entry.get()
        device = device_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        if person and device and start_date and end_date:
            tree.insert('', tk.END, values=(person, device, start_date, end_date))
            add_window.destroy()
        else:
            messagebox.showwarning("输入错误", "所有字段都必须填写。")

    add_window = tk.Toplevel(root)
    add_window.title("添加条目")

    tk.Label(add_window, text="人物").grid(row=0, column=0)
    person_entry = ttk.Entry(add_window)
    person_entry.grid(row=0, column=1)

    tk.Label(add_window, text="设备名称").grid(row=1, column=0)
    device_entry = ttk.Entry(add_window)
    device_entry.grid(row=1, column=1)

    tk.Label(add_window, text="开始时间").grid(row=2, column=0)
    start_date_entry = DateEntry(add_window, date_pattern='yyyy-mm-dd')
    start_date_entry.grid(row=2, column=1)

    tk.Label(add_window, text="结束时间").grid(row=3, column=0)
    end_date_entry = DateEntry(add_window, date_pattern='yyyy-mm-dd')
    end_date_entry.grid(row=3, column=1)

    tk.Button(add_window, text="添加", command=add_data).grid(row=4, column=0, columnspan=2)

# 添加条目按钮
add_button = tk.Button(button_frame, text="添加条目", command=add_entry)
add_button.pack(side=tk.LEFT, padx=5, pady=5)

# 启动时加载数据
load_data()

# 运行主窗口
root.mainloop()
