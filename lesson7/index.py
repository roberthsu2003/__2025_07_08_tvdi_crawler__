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
        
        # 建立root_left_frame來包含左側的內容 
        root_left_frame = tk.Frame(self.root)
        root_left_frame.pack(side=tk.LEFT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 建立左側的標題
        # left_title的文字靠左        
        left_title = tk.Label(root_left_frame, text="請選擇股票(可多選)", font=("Arial"), anchor="w", justify="left")
        left_title.pack(pady=(10,0), fill=tk.X,padx=10)

        # 建立leftFrame來包含 listbox 和 scrollbar
        left_frame = tk.Frame(root_left_frame)
        left_frame.pack(pady=10, padx=10,fill=tk.BOTH, expand=True)

        

        # 增加left_frame內的內容
        self.scrollbar = tk.Scrollbar(left_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.stock_listbox = tk.Listbox(left_frame,
                                        selectmode=tk.MULTIPLE,
                                        yscrollcommand=self.scrollbar.set,
                                        width=15,
                                        height=20)
        
        # 手動插入股票資料
        for stock in self.stock_codes:
            self.stock_listbox.insert(tk.END, f"{stock['code']} - {stock['name']}")
            
        self.stock_listbox.pack(side=tk.LEFT)
        self.scrollbar.config(command=self.stock_listbox.yview)

        # 在左下方建立一個取消按鈕
        # 取消按鈕的功能是取消self.stock_listbox的選取

        cancel_button = tk.Button(root_left_frame, text="取消", command=self.clear_selection)
        cancel_button.pack(side=tk.BOTTOM, pady=10)

        # 建立root_right_frame來包含選取股票的資訊
        root_right_frame = tk.Frame(self.root)
        root_right_frame.pack(side=tk.RIGHT, pady=10,padx=10,fill=tk.BOTH, expand=True)

        # 在右側顯示選取的股票資訊
        self.selected_label = tk.Label(root_right_frame, text="選取的股票資訊", font=("Arial", 16, "bold"))
        self.selected_label.pack(pady=10)


    


    def clear_selection(self):
        self.stock_listbox.selection_clear(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()