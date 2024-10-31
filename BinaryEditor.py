import tkinter as tk
from tkinter import filedialog
import binascii
import os


class BinaryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Editor")

        self.text = tk.Text(self.root)
        self.text.pack(expand=True, fill=tk.BOTH)

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

        # 添加文件大小顯示的標籤
        self.info_label = tk.Label(
            self.root, text="File Size: 0 bytes      |      Page 0 / 0")
        self.info_label.pack(side=tk.BOTTOM)

        # 添加上一頁和下一頁的按鈕
        self.prev_button = tk.Button(
            self.root, text="Previous Page", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(
            self.root, text="Next Page", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT)

        # 添加設定每一頁能顯示多少byte
        self.page_size_entry = tk.Entry(self.root)
        self.page_size_entry.pack(side=tk.TOP)
        self.page_size_entry.insert(0, "1024")  # 預設值

        self.set_page_size_button = tk.Button(
            self.root, text="Set Page Size", command=self.set_page_size)
        self.set_page_size_button.pack(side=tk.BOTTOM)

        # 各種變數
        self.file_path = None
        self.file = None
        self.data = bytearray(b'')       # 儲存整份檔案
        self.page_size = 1024   # 每頁的大小
        self.current_page = 0   # 當前頁數
        self.total_pages = 0    # 總頁數
        self.file_size = 0      # 文件大小

    # 打開檔案
    def open_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.text.delete(1.0, tk.END)   # 清空顯示內容

            self.file = open(self.file_path, 'rb')
            binary_data = self.file.read()
            self.data = bytearray(binary_data)

            # 獲取檔案大小並計算總共需要幾頁
            self.file_size = os.path.getsize(self.file_path)
            self.total_pages = (
                self.file_size + self.page_size - 1) // self.page_size

            self.current_page = 0  # 重置到第一頁
            self.show_page(self.current_page)

    # 顯示這一頁
    def show_page(self, page_num):
        if self.file:
            # 計算文件應該讀取的開始位置
            start = page_num * self.page_size

            # 取出本頁應顯示的內容
            page = self.data[start: start+self.page_size]

            # 清空文本框並顯示當前頁內容
            self.text.delete(1.0, tk.END)
            hex_page = binascii.hexlify(page).decode('utf-8')

            # 以空格分開每個byte
            spaced_hex_page = ' '.join(
                hex_page[i:i+2] for i in range(0, len(hex_page), 2))

            # 顯示內容
            self.text.insert(tk.END, spaced_hex_page)

            # 更新資訊標籤
            self.update_info_label()

            # 更新按鈕狀態
            self.update_buttons()

    # 更新self.data所儲存的整份檔案資料
    def update_data(self, page_num):
        hex_data = self.text.get(1.0, tk.END).replace(' ', '').strip()
        last_page_size = self.file_size - (self.total_pages-1) * self.page_size
        # 若此頁大小不夠，加上空字符
        if (page_num+1 != self.total_pages):
            while (len(hex_data) < 2*self.page_size):
                hex_data += '00'
        else:
            while (len(hex_data) < 2*last_page_size):
                hex_data += '00'

        # 將文字框數據寫入self.data
        hex_data.encode('utf-8')
        binary_data = binascii.unhexlify(hex_data)
        start = page_num * self.page_size
        self.data[start: start+self.page_size] = bytearray(binary_data)

    def next_page(self):
        self.update_data(self.current_page)
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def prev_page(self):
        self.update_data(self.current_page)
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def set_page_size(self):
        try:
            # 讀取用戶輸入的 page size，並更新屬性
            new_page_size = int(self.page_size_entry.get())
            if new_page_size <= 0:
                raise ValueError("Page size must be a positive integer.")
            self.page_size = new_page_size

            # 重新計算總頁數
            if self.file_size > 0:
                self.total_pages = (
                    self.file_size + self.page_size - 1) // self.page_size
                self.current_page = min(
                    self.current_page, self.total_pages - 1)  # 確保當前頁不超出範圍
                self.show_page(self.current_page)  # 更新顯示頁面
                self.update_info_label()  # 更新資訊標籤
        except ValueError as e:
            print(f"Error: {e}")

    def update_buttons(self):
        # 如果在第一頁，禁用“上一頁”按鈕
        if self.current_page == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)

        # 如果在最後一頁，禁用“下一頁”按鈕
        if self.current_page == self.total_pages - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)

    def update_info_label(self):
        # 更新資訊標籤
        self.info_label.config(
            text=f"File Size: {self.file_size} bytes      |      Page {self.current_page + 1} / {self.total_pages}")

    def write_to_file(self, path):
        self.update_data(self.current_page)
        try:
            # 打開文件並寫入數據
            with open(path, 'wb+') as f:
                f.write(self.data)
            print(f"File saved successfully to {path}!")
        except binascii.Error:
            print("Error: Invalid hexadecimal data.")

    # 儲存
    def save_file(self):
        if self.file:
            self.write_to_file(self.file_path)

    # 另存新檔
    def save_file_as(self):
        new_file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[
            ("Binary files", "*.bin"), ("Image files", "*.png"), ("All files", "*.*")])
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
