import tkinter as tk
from tkinter import filedialog
from uds_main import *


# 简单的 Tkinter 界面：只有一个字符串输入框和一个运行按钮


def run_tool():
    req_id = int(entry_req_id.get(),16)
    resp_id = int(entry_resp_id.get(),16)
    req_id_app = int(entry_req_id_app.get(),16)
    resp_id_app = int(entry_resp_id_app.get(),16)
    can_type = can_type_var.get()
    if can_type == "classic":
        fd_flag = False
    elif can_type == "canfd":
        fd_flag= True
    frame_len = int(frame_len_var.get())
    print("req id is %d, resp id is %d, can type is %s, frame length is %d" %(req_id,resp_id,can_type,frame_len))
    print("dll file path is %s" %(dll_path.get()))
    print("flash driver file path is %s" %(flashdrv_hex_path.get()))
    print("flash driver sig path is %s" %(flashdrv_sig_path.get()))
    print("target hex path is %s" %(target_hex_path.get()))
    print("target sig path is %s" %(target_sig_path.get()))
    uds_program_init(req_id,resp_id,req_id_app,resp_id_app,fd_flag,frame_len,dll_path.get())
    uds_program_main(flashdrv_hex_path.get(),flashdrv_sig_path.get(),target_hex_path.get(),target_sig_path.get())

def run_stayinboot():
    req_id = int(entry_req_id.get(),16)
    resp_id = int(entry_resp_id.get(),16)
    req_id_app = int(entry_req_id_app.get(),16)
    resp_id_app = int(entry_resp_id_app.get(),16)
    can_type = can_type_var.get()
    if can_type == "classic":
        fd_flag = False
    elif can_type == "canfd":
        fd_flag= True
    frame_len = int(frame_len_var.get())
    uds_program_init(req_id,resp_id,req_id_app,resp_id_app,fd_flag,frame_len,dll_path.get())
    uds_program_stayinboot()

def choose_dll_file():
    path = filedialog.askopenfilename(title="选择文件")
    if path:
        dll_path.set(path)  # 更新绑定变量
        dll_display.config(text=path) 

def choose_flashdrv_hex_file():
    path = filedialog.askopenfilename(title="选择文件")
    if path:
        flashdrv_hex_path.set(path)  # 更新绑定变量
        flashdrv_hex_display.config(text=path) 

def choose_flashdrv_sig_file():
    path = filedialog.askopenfilename(title="选择文件")
    if path:
        flashdrv_sig_path.set(path)  # 更新绑定变量
        flashdrv_sig_display.config(text=path) 

def choose_target_hex_file():
    path = filedialog.askopenfilename(title="选择文件")
    if path:
        target_hex_path.set(path)  # 更新绑定变量
        target_hex_display.config(text=path) 

def choose_target_sig_file():
    path = filedialog.askopenfilename(title="选择文件")
    if path:
        target_sig_path.set(path)  # 更新绑定变量
        target_sig_display.config(text=path) 

root = tk.Tk()
root.title("python program")
root.geometry("350x500")
row_index = 0


tk.Label(root, text="Boot Request Frame ID(HEX):").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
entry_req_id = tk.Entry(root, width=5)
entry_req_id.grid(row=row_index, column=1, padx=10)
row_index += 1

tk.Label(root, text="Boot Response Frame ID(HEX):").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
entry_resp_id = tk.Entry(root, width=5)
entry_resp_id.grid(row=row_index, column=1, padx=10)
row_index += 1

tk.Label(root, text="APP Request Frame ID(HEX):").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
entry_req_id_app = tk.Entry(root, width=5)
entry_req_id_app.grid(row=row_index, column=1, padx=10)
row_index += 1

tk.Label(root, text="APP Response Frame ID(HEX):").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
entry_resp_id_app = tk.Entry(root, width=5)
entry_resp_id_app.grid(row=row_index, column=1, padx=10)
row_index += 1

tk.Label(root, text="CAN 类型：").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
can_options = ["canfd", "classic"]
can_type_var = tk.StringVar(value=can_options[0])
tk.OptionMenu(root, can_type_var, *can_options).grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
row_index += 1

tk.Label(root, text="报文长度：").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
frame_len_options = [8,12,16,20,24,32,48,64]
frame_len_var = tk.StringVar(value=frame_len_options[0])
tk.OptionMenu(root, frame_len_var, *frame_len_options).grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
row_index += 1

tk.Label(root, text="选择seed/key dll文件:").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
dll_path = tk.StringVar()
tk.Button(root, text="浏览", command=choose_dll_file).grid(row=row_index, column=1, sticky="w", padx=10)
dll_display = tk.Label(root, text="未选择文件", fg="gray")
dll_display.grid(row=row_index, column=2, sticky="w", padx=10)
row_index += 1

tk.Label(root, text="选择seed/key flashdrv_hex文件:").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
flashdrv_hex_path = tk.StringVar()
tk.Button(root, text="浏览", command=choose_flashdrv_hex_file).grid(row=row_index, column=1, sticky="w", padx=10)
flashdrv_hex_display = tk.Label(root, text="未选择文件", fg="gray")
flashdrv_hex_display.grid(row=row_index, column=2, sticky="w", padx=10)
row_index += 1

tk.Label(root, text="选择seed/key flashdrv_sig文件:").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
flashdrv_sig_path = tk.StringVar()
tk.Button(root, text="浏览", command=choose_flashdrv_sig_file).grid(row=row_index, column=1, sticky="w", padx=10)
flashdrv_sig_display = tk.Label(root, text="未选择文件", fg="gray")
flashdrv_sig_display.grid(row=row_index, column=2, sticky="w", padx=10)
row_index += 1

tk.Label(root, text="选择seed/key target_hex文件:").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
target_hex_path = tk.StringVar()
tk.Button(root, text="浏览", command=choose_target_hex_file).grid(row=row_index, column=1, sticky="w", padx=10)
target_hex_display = tk.Label(root, text="未选择文件", fg="gray")
target_hex_display.grid(row=row_index, column=2, sticky="w", padx=10)
row_index += 1

tk.Label(root, text="选择seed/key target_sig文件:").grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
target_sig_path = tk.StringVar()
tk.Button(root, text="浏览", command=choose_target_sig_file).grid(row=row_index, column=1, sticky="w", padx=10)
target_sig_display = tk.Label(root, text="未选择文件", fg="gray")
target_sig_display.grid(row=row_index, column=2, sticky="w", padx=10)
row_index += 1

tk.Button(root, text="运行刷写", command=run_tool).grid(row=row_index, column=0, columnspan=2, pady=10)
row_index += 1
tk.Button(root, text="运行stayinboot", command=run_stayinboot).grid(row=row_index, column=0, columnspan=2, pady=10)
row_index += 1

root.mainloop()