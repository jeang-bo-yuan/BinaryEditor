"""
這模組提供了用於顯示二進制資料的表格
"""
import tkinter as tk
import re
import math

DEBUG_MODE = False


class BinTable(tk.Frame):
    """
    顯示二進制資料的表格，大小為 size * size，每一個格子都是一個 tk.Entry。
    用法：
    - 初始化時傳入 data、size （初始化後可用 setData()、resize() 來修改）
    - nextPage()、prevPage()換頁（頁面的範圍 0 ~ getMaxPage()）

    Getter:
    - getData() : 取得資料
    - getMaxPage() : 最大的頁數
    - getPageNum() : 取得頁數

    Highlight:
    - clearHighlights() : 清除所有的標記
    - highlight() : 將「資料」中某段範圍給標記
    """
    # constants ##########################
    HEX_VALIDATOR: tuple

    # private members ####################
    m_data: bytearray                  # 檔案的資料
    m_data_hilit: list[bool]           # 記錄檔案中哪些資料被標記（大小和 m_data 一樣大）
    m_entries: list[tk.Entry] | None   # 大小為 m_size * m_size，只包含「顯示出來」的格子（以Row Major的方式儲存）
    m_page: int        # 目前在的頁數
    m_max_page: int    # 最大頁數
    m_size: int        # 每頁表格的大小

    def __init__(self, parent: tk.Misc, data: bytearray = [], size: int = 10):
        """
        初始化。父 widget 為 parent，一開始顯示的內容為 data，表格大小為 size * size。
        """
        tk.Frame.__init__(self, parent)
        self.__init_validator__()

        self.m_data = bytearray(data)
        self.m_data_hilit = [False for _ in range(len(self.m_data))]
        self.m_entries = None
        self.m_page = 0
        self.m_max_page = 0
        self.m_size = 0
        self.resize(size)

    def __init_validator__(self):
        """
        初始化entry的validator（用來確認輸入的格式）
        """
        def isHex(num):
            return re.match("^[0-9a-fA-F]{0,2}$", num) is not None
        self.HEX_VALIDATOR = (self.register(isHex), "%P")

    def __write_back__(self):
        """
        將表格的內容寫回m_data
        """
        for row in range(self.m_size):
            for col in range(self.m_size):
                # 表格的index
                idx = (row * self.m_size) + col
                # 對應原陣列中的哪個byte
                src_idx = idx + self.m_page * self.m_size * self.m_size

                # 超出範圍
                if src_idx >= len(self.m_data):
                    break

                try:
                    self.m_data[src_idx] = int(
                        self.m_entries[idx].get(), base=16)
                except ValueError:
                    self.m_data[src_idx] = 0

        if DEBUG_MODE:
            print(self.m_data)

    def __update_content__(self):
        """
        當「m_data」或「table大小」有變動時呼叫
        1. 更新m_max_page的值
        2. 依據m_data來更新表格顯示的內容
        """
        if len(self.m_data) == 0:
            self.m_max_page = 0
        else:
            self.m_max_page = (len(self.m_data) - 1) // (self.m_size * self.m_size)

        page_start = self.m_page * len(self.m_entries)  # 目前的頁面的第一個 byte 在 m_data 的 index

        # 對於每個格子
        for entry_idx, entry in enumerate(self.m_entries):
            # 清空內容
            entry.delete(0, tk.END)
            
            # 如果該格子沒有在 m_data 中對應的資料
            if (data_idx := page_start + entry_idx) >= len(self.m_data):
                entry.configure(state=tk.DISABLED)
            else:
                # 重設背景
                entry.configure(background=self.__bg__(entry_idx))
                # 啟用
                entry.configure(state=tk.NORMAL)
                # 設置內容
                txt = "%02x" % self.m_data[data_idx]
                entry.insert(0, txt)                   


    def __bg__(self, entry_idx: int):
        """ 取得self.m_entries[entry_idx] 的背景顏色 """
        data_idx = self.m_page * len(self.m_entries) + entry_idx # 該格子對應到 m_data 中的哪個資料

        if data_idx < len(self.m_data_hilit) and self.m_data_hilit[data_idx]:
            return "yellow"
        elif (entry_idx // self.m_size + entry_idx % self.m_size) % 2:
            return "gray81"
        else:
            return "white"

    def resize(self, new_size: int):
        """
        重新調整大小
        """
        if self.m_size == new_size: # 大小不變，忽略
            return
        
        # 刪掉舊的表格
        if self.m_entries is not None:
            for entry in self.m_entries:
                entry.destroy()

        # 建立新的表格，Row Major
        self.m_entries = list()
        for row in range(new_size):
            for col in range(new_size):
                self.rowconfigure(row, weight=1)     # 自動調整大小
                self.columnconfigure(col, weight=1)

                # 新的格子
                self.m_entries.append(tk.Entry(self, width=4, borderwidth=1,
                                               validate='key', validatecommand=self.HEX_VALIDATOR))
                self.m_entries[-1].grid(row=row, column=col,
                                        sticky=(tk.W, tk.E, tk.S, tk.N))

        # 變小，將表格外的區域的weight設成0
        if new_size < self.m_size:
            for r in range(new_size, self.m_size):
                self.rowconfigure(r, weight=0)

            for c in range(new_size, self.m_size):
                self.columnconfigure(c, weight=0)

        self.m_size = new_size
        self.__update_content__()

    def setData(self, data: bytearray):
        """
        重新設定data
        """
        self.m_data = bytearray(data)
        self.m_data_hilit = [False for _ in range(len(self.m_data))] # 清空選擇
        self.m_page = 0
        self.__update_content__()

    def nextPage(self, *args):
        """
        頁數加1
        """
        if self.m_page == self.m_max_page: # 沒有下一頁
            return
        
        self.__write_back__()

        self.m_page += 1
        if DEBUG_MODE:
            print(f'Page: {self.m_page}')

        self.__update_content__()

    def prevPage(self, *args):
        """
        頁數減1
        """
        if (self.m_page == 0):
            return

        self.__write_back__()

        self.m_page -= 1
        if DEBUG_MODE:
            print(f'Page: {self.m_page}')

        self.__update_content__()

    def getData(self) -> bytearray:
        """
        取得經修改後的資料
        """
        self.__write_back__()
        return self.m_data

    def getMaxPage(self):
        """
        回傳最大頁數
        """
        return self.m_max_page

    def getPageNum(self) -> int:
        """
        取得目前在的頁數
        """
        return self.m_page

    def clearHighlights(self, event=None):
        """ 清除所有高亮顯示 """
        self.m_data_hilit = [False for _ in range(len(self.m_data))]
        for i, entry in enumerate(self.m_entries):
            entry.configure(background=self.__bg__(i))

    def highlight(self, start: int, end: int):
        """ 將 data 中 [start, end) 的範圍標記起來 """
        page_size = len(self.m_entries)      # 目前的頁面可以放幾個 bytes
        page_start = self.m_page * page_size # 這一頁的第一個 byte 在 m_data 的 index

        for idx in range(start, end):
            self.m_data_hilit[idx] = True

            # 如果 m_data[idx] 顯示在目前的頁面
            if (entry_idx := idx - page_start) < page_size and entry_idx >= 0:
                self.m_entries[entry_idx].configure(background=self.__bg__(entry_idx))

