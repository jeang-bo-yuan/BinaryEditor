"""
這個模組提供了class SelectRange，以記錄選取的範圍
"""
import math

class SelectRange:
    """
    這個class用了兩個變數來記錄選取的範圍（start和end）
    
    選取：
    - selectSingle() : 選擇單一個點
    - setEnd()       : 設定選擇範圍的終點
    - unselect()     : 將選擇範圍設成None

    存取：
    - contain()      : 確認範圍內有沒有特定的點
    - toTuple()      : 將選取範圍轉成一個有序數組（ordered tuple）
    """
    # private member #################
    m_start: int | None
    m_end: int | None

    def __init__(self):
        self.m_start = None
        self.m_end = None

    # 選取 ################################################################################################
    def selectSingle(self, idx: int):
        """
        將選取範圍限縮在單一個點上
        """
        self.m_start = self.m_end = idx
        print(f"Select: {self.toTuple()}")

    def setEnd(self, idx: int):
        """
        設定選取範圍的終點（如果原本沒有選取任何東西則和selectSingle一樣）
        """
        if self.m_start is None:
            self.m_start = idx
        self.m_end = idx
        print(f"Select: {self.toTuple()}")

    def unselect(self):
        """
        取消選取
        """
        self.m_start = self.m_end = None

    # 存取 ###########################################################################################
    def contain(self, idx: int):
        """
        確認 idx 有沒有在選取範圍內
        """
        if self.m_start is None:
            return
        
        # 從起點到終點的向量
        L = self.m_end - self.m_start
        # 從起點到 idx 的向量
        D = idx        - self.m_start

        # 如果            L 和 D 同方向，且 L 比 D 長
        return D == 0 or (math.copysign(L, D) == L and abs(D) <= abs(L))

    def toTuple(self, low=0, high=math.inf) -> tuple[int, int] | None:
        """
        將選取範圍轉成一個有序數組（ordered tuple）。
        參數 low, high 用來將回傳值給 clamp 到 [low, high) 的範圍。
        """
        if self.m_start is None:
            return None
        
        a = min(self.m_start, self.m_end)
        b = max(self.m_start, self.m_end)

        # 分別將 a, b clamp 到 [low, high - 1) 的範圍
        a = min(max(low, a), high - 1)
        b = min(max(low, b), high - 1)

        return (a, b)


