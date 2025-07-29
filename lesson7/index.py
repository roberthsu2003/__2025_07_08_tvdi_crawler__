import tkinter as tk

try:
    import wantgoo
except ImportError:
    raise ImportError("請確保已安裝 wantgoo 模組，或將 wantgoo.py 放在相同目錄下。")

class SimpleApp:
    def __init__(self, root):
        self.root = root
        try:
            self.stock_codes: list[dict] = wantgoo.get_stocks_with_twstock()
            if not isinstance(self.stock_codes, list):
                raise ValueError("wantgoo.get_stocks_with_twstock() 應回傳一個股票字典的 list。")
        except Exception as e:
            self.stock_codes = []
            print(f"取得股票資料時發生錯誤: {e}")


        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="即時股票資訊", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)        
        
        # 建立框架來包含 listbox 和 scrollbar
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 建立捲動列
        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        #self.stock_listbox無法改變寬度,width=50沒有作用
        
        self.stock_listbox = tk.Listbox(frame,
                                        selectmode=tk.MULTIPLE,
                                        yscrollcommand=self.scrollbar.set,
                                        width=15,
                                        height=20)
        
        # 手動插入股票資料
        for stock in self.stock_codes:
            self.stock_listbox.insert(tk.END, f"{stock['code']} - {stock['name']}")
            
        self.stock_listbox.pack(side=tk.LEFT)
        self.scrollbar.config(command=self.stock_listbox.yview)


    


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()