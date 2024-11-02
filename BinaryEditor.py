"""
主程式
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
# import binascii
import os
import math

import BinTable


class BinaryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Editor")
        self.file_opened = False  # 新增布林變數以追踪檔案狀態

        # 修改：原本的text改成table
        self.table = BinTable.BinTable(self.root)
        self.table.pack(expand=True, fill=tk.BOTH)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # 添加選單按鈕
        file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_command(label="Search", command=self.search)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)

        # 清除標記
        self.root.bind("<Escape>", self.table.clearHighlights)

        # 添加 Page Size 選單
        page_size_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Page Size", menu=page_size_menu)

        # 頁面大小選項
        for size in [10, 20, 30]:
            page_size_menu.add_command(
                label=f"{size} x {size} bytes", command=lambda s=size: self.set_page_size(s))

        # 添加文件大小顯示的標籤
        self.info_label = tk.Label(
            self.root, text="File Size: 0 bytes      |      Page 1 / 1")
        self.info_label.pack(side=tk.BOTTOM)

        # 添加上一頁和下一頁的按鈕
        self.prev_button = tk.Button(
            self.root, text="Previous Page", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(
            self.root, text="Next Page", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT)

        # 各種變數
        self.file_path = None
        self.file = None

        # 更新按鈕
        self.update_buttons()

    # 打開檔案
    def open_file(self):
        self.file_path = filedialog.askopenfilename(initialdir='.')
        if self.file_path:
            # 改標題
            self.root.title(
                f"Binary Editor ({os.path.relpath(self.file_path, '.')})")
            
            # 讀檔，然後傳進table中
            self.file = open(self.file_path, 'rb')
            binary_data = self.file.read()
            self.table.setData(binary_data)

            self.file_opened = True
            self.update_buttons()
            self.update_info_label()

    def next_page(self):
        self.table.nextPage()
        self.update_buttons()
        self.update_info_label()

    def prev_page(self):
        self.table.prevPage()
        self.update_buttons()
        self.update_info_label()

    def set_page_size(self, size):
        try:
            self.table.resize(size)
        except ValueError as e:
            print(f"Error: {e}")

        self.update_buttons()
        self.update_info_label()

    def update_buttons(self):
        # 如果在第一頁，禁用“上一頁”按鈕
        if self.table.getPageNum() == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)

        if self.table.getPageNum() == self.table.getMaxPage():
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)

    def update_info_label(self):
        # 更新資訊標籤
        self.info_label.config(
            text=f"File Size: {len(self.table.getData())} bytes      |      Page {self.table.getPageNum()+1} / {self.table.getMaxPage()+1}")

    def write_to_file(self, path):
        # 打開文件並寫入數據
        with open(path, 'wb+') as f:
            f.write(self.table.getData())
        print(f"File saved successfully to {path}!")

    # 儲存
    def save_file(self):
        if self.file:
            self.write_to_file(self.file_path)

    # 另存新檔
    def save_file_as(self):
        new_file_path = filedialog.asksaveasfilename(defaultextension=".bin", initialdir='.',
                                                     filetypes=[("Binary files", "*.bin"), ("Image files", "*.png"), ("All files", "*.*")])
        if new_file_path:
            self.write_to_file(new_file_path)

    # 搜尋
    def search(self):
        # 使用 simpledialog 顯示輸入框
        if self.file_opened:
            search_term = simpledialog.askstring(
                "Input", "Enter search term:", parent=self.root)

            if search_term:
                # 將搜索字符轉換為 bytes
                search_bytes = search_term.encode('utf-8')

                # 獲取當前的二進制數據
                binary_data = self.table.getData()

                # 清除之前的標記
                self.table.clearHighlights()

                # 查找字符並標記
                start_index = 0
                while True:
                    start_index = binary_data.find(search_bytes, start_index)
                    if start_index == -1:
                        break

                    # 標記找到的字元為黃色
                    self.table.highlight(
                        start_index, start_index + len(search_bytes))
                    start_index += len(search_bytes)  # 移動到下一個搜索位置

                print(f"Searching for: {search_term}")
        else:
            alert = tk.Toplevel(self.root)
            alert.title("Alert")

            label = tk.Label(alert, text="No file opened!")
            label.pack(padx=20, pady=20)

            # 按鈕來關閉警示視窗
            close_button = tk.Button(
                alert, text="Close", command=alert.destroy)
            close_button.pack(side="bottom")
            self.center_window(alert)

            # 讓alert顯示在上層，https://stackoverflow.com/questions/16803686/how-to-create-a-modal-dialog-in-tkinter
            alert.wait_visibility()
            alert.grab_set()
            alert.transient(self.root)

    # 視窗位置
    def center_window(self, window):
        window.update_idletasks()  # 更新窗口以獲取正確的大小
        width = window.winfo_width()
        height = window.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")

    # 離開
    def exit_application(self):
        if self.file:  # 如果有打開的文件，先關閉它
            self.file.close()
        self.root.quit()  # 結束主事件循環
        self.root.destroy()  # 銷毀窗口


if __name__ == "__main__":
    root = tk.Tk()
    editor = BinaryEditor(root)
    root.geometry("400x300")  # 設定主視窗的大小
    root.mainloop()
