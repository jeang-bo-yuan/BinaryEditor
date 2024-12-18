"""
提供了類別 ByteNumStr，來進行字串和 byte 間的轉換
"""
import re
import tkinter as tk

class ByteNumStr:
    """ 在字串和 byte 間轉換 """
    m_bin_tk_validator: tuple | None
    m_oct_tk_validator: tuple | None
    m_dec_tk_validator: tuple | None
    m_hex_tk_validator: tuple | None
    m_base: int

    def __init__(self, base = 16):
        """ 初始化，但不初始化 validator """
        self.m_bin_tk_validator = None
        self.m_oct_tk_validator = None
        self.m_dec_tk_validator = None
        self.m_hex_tk_validator = None
        self.m_base = base
    
    def setBase(self, newBase: int):
        """ 改變base """
        self.m_base = newBase

    # Convert ##################################################################
    def toString(self, num: int):
        """ 依據目前的base，將num轉成string """
        assert type(num) == int

        if self.m_base == 2:
            # 顯示8個bit。若不夠，則最高位補0
            return "{:0>8}".format(  bin(num)[2:]  )
        if self.m_base == 8:
            return "%03o" % num
        if self.m_base == 10:
            return "%d" % num
        if self.m_base == 16:
            return "%02x" % num
        
        raise RuntimeError(f"Unsupported Base: {self.m_base}")
        
    def toInt(self, num: str):
        """ 依據目前的base，將num轉int """
        assert type(num) == str

        return int(num, base=self.m_base)
    
    # Tk ###################################################################################################
    def initValidator(self, TK: tk.Misc):
        """
        初始化給`tk.Entry`用的validator（用來確認輸入的格式）
        """
        def isBin(num):
            return re.match("^[01]{0,8}$", num) is not None
        self.m_bin_tk_validator = (TK.register(isBin), "%P")

        def isOct(num):
            if num == "": return True
            return (re.match("^[0-7]{1,3}$", num) is not None) and int(num, base=8) <= 255
        self.m_oct_tk_validator = (TK.register(isOct), "%P")

        def isDec(num):
            if num == "": return True
            return (re.match("^[0-9]{1,3}$", num) is not None) and int(num, base=10) <= 255
        self.m_dec_tk_validator = (TK.register(isDec), "%P")

        def isHex(num):
            return re.match("^[0-9a-fA-F]{0,2}$", num) is not None
        self.m_hex_tk_validator = (TK.register(isHex), "%P")

    def getValidator(self):
        """ 取得目前base下適用的validator """
        if self.m_base == 2:
            return self.m_bin_tk_validator
        if self.m_base == 8:
            return self.m_oct_tk_validator
        if self.m_base == 10:
            return self.m_dec_tk_validator
        if self.m_base == 16:
            return self.m_hex_tk_validator
        
        raise RuntimeError(f"Unsupported Base: {self.m_base}")

