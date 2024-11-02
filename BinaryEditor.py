"""
主程式
"""
import tkinter as tk
from tkinter import filedialog
# import binascii
import os

import BinTable


class BinaryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Editor")

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
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)

        # 添加 Page Size 選單
        page_size_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Page Size", menu=page_size_menu)

        # 頁面大小選項
        for size in [10, 20, 30, 40]:
            page_size_menu.add_command(
                label=f"{size} bytes", command=lambda s=size: self.set_page_size(s))

        # 添加文件大小顯示的標籤
        self.info_label = tk.Label(
            self.root, text="File Size: 0 bytes      |      Page 0")
        self.info_label.pack(side=tk.BOTTOM)

        # 添加上一頁和下一頁的按鈕
        self.prev_button = tk.Button(
            self.root, text="Previous Page", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(
            self.root, text="Next Page", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT)

# =============================================================================
#         # 添加設定每一頁能顯示多少byte
#         self.page_size_entry = tk.Entry(self.root)
#         self.page_size_entry.pack(side=tk.TOP)
#         self.page_size_entry.insert(0, "10")  # 預設值
#         # 修改：按下 Enter 後觸發 set_page_size
#         self.page_size_entry.bind("<Return>", lambda x: self.set_page_size())
#
#         self.set_page_size_button = tk.Button(
#             self.root, text="Set Page Size", command=self.set_page_size)
#         self.set_page_size_button.pack(side=tk.BOTTOM)
# =============================================================================

        # 各種變數
        self.file_path = None
        self.file = None

        # 更新按鈕
        self.update_buttons()

    # 打開檔案

    def open_file(self):
        self.file_path = filedialog.askopenfilename(initialdir='.')
        if self.file_path:
            # self.table.delete(1.0, tk.END)   # 清空顯示內容
            self.root.title(
                f"Binary Editor ({os.path.relpath(self.file_path, '.')})")

            self.file = open(self.file_path, 'rb')
            binary_data = self.file.read()
            self.table.setData(binary_data)

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

    def update_buttons(self):
        # 如果在第一頁，禁用“上一頁”按鈕
        if self.table.getPageNum() == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)

    def update_info_label(self):
        # 更新資訊標籤
        self.info_label.config(
            text=f"File Size: {len(self.table.getData())} bytes      |      Page {self.table.getPageNum()}")

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

    # 離開
    def exit_application(self):
        if self.file:  # 如果有打開的文件，先關閉它
            self.file.close()
        self.root.quit()  # 結束主事件循環
        self.root.destroy()  # 銷毀窗口


if __name__ == "__main__":
    root = tk.Tk()
    editor = BinaryEditor(root)
    root.mainloop()
