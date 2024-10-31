"""
這模組提供了用於顯示二進制資料的表格
"""
import tkinter as tk
import re

DEBUG_MODE = False

class BinTable(tk.Frame):
    """
    顯示二進制資料的表格，大小為 size * size，每一個格子都是一個 tk.Entry。
    用法：
    - 初始化時傳入 data、size （初始化後可用 setData()、resize() 來修改）
    - nextPage()、prevPage()換頁
    
    Getter:
    - getData() : 取得資料
    - getPageNum() : 取得頁數
    """
    # constants ##########################
    HEX_VALIDATOR: tuple
    
    # private members ####################
    m_data: bytearray
    m_entries: list[tk.Entry] | None
    m_page: int
    m_size: int
    

    def __init__(self, parent: tk.Misc, data: bytearray = [], size: int = 10):
        """
        初始化。父 widget 為 parent，一開始顯示的內容為 data，表格大小為 size * size。
        """
        tk.Frame.__init__(self, parent)
        self.__init_validator__()

        self.m_data = bytearray(data)
        self.m_entries = None
        self.m_page = 0
        self.resize(size)

        if DEBUG_MODE:
            self.winfo_toplevel().bind("<Control-p>", self.prevPage)
            self.winfo_toplevel().bind("<Control-n>", self.nextPage)
        

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
                if src_idx >= len(self.m_data):  break
                
                try:
                    self.m_data[src_idx] = int(self.m_entries[idx].get(), base=16)
                except ValueError:
                    self.m_data[src_idx] = 0
        
        if DEBUG_MODE: print(self.m_data)
                


    def __update_content__(self):
        """
        依據m_data來更新表格顯示的內容
        """
        for row in range(self.m_size):
            for col in range(self.m_size):
                # 表格的index
                idx = (row * self.m_size) + col
                # 對應原陣列中的哪個byte
                src_idx = idx + self.m_page * self.m_size * self.m_size

                # 清空內容
                self.m_entries[idx].delete(0, tk.END)

                if src_idx >= len(self.m_data):
                    # 停用
                    self.m_entries[idx].configure(state=tk.DISABLED)
                else:
                    # 設置內容
                    self.m_entries[idx].configure(state=tk.NORMAL)
                    txt = "%02x" % self.m_data[src_idx]
                    self.m_entries[idx].insert(0, txt)


    def resize(self, new_size: int):
        """
        重新調整大小
        """
        self.m_size = new_size

        # 刪掉舊的表格
        if self.m_entries is not None:
            for entry in self.m_entries:
                entry.destroy()

        # 建立新的表格
        self.m_entries = list()
        for row in range(new_size):
            for col in range(new_size):
                self.rowconfigure(row, weight=1)     # 自動調整大小
                self.columnconfigure(col, weight=1)

                # 新的格子
                self.m_entries.append(tk.Entry(self, width=4, borderwidth=1,
                                               validate= 'key', validatecommand= self.HEX_VALIDATOR,
                                               background="gray81" if (row + col)&1 else "white"))
                self.m_entries[-1].grid(row=row, column=col, sticky=(tk.W, tk.E, tk.S, tk.N))
        
        self.__update_content__()

    def setData(self, data: bytearray):
        """
        重新設定data
        """
        self.m_data = bytearray(data)
        self.m_page = 0
        self.__update_content__()


    def nextPage(self, *args):
        """
        頁數加1
        """
        self.__write_back__()

        self.m_page += 1
        if DEBUG_MODE: print(f'Page: {self.m_page}')

        self.__update_content__()

    def prevPage(self, *args):
        """
        頁數減1
        """
        if (self.m_page == 0): return

        self.__write_back__()
        
        self.m_page -= 1
        if DEBUG_MODE: print(f'Page: {self.m_page}')

        self.__update_content__()


    def getData(self) -> bytearray:
        """
        取得經修改後的資料
        """
        self.__write_back__()
        return self.m_data
    
    def getPageNum(self) -> int:
        """
        取得目前在的頁數
        """
        return self.m_page
