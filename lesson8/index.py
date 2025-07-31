import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import wantgoo


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

        self.selected_stocks: list[str] = []

        self.create_widgets()

    def create_widgets(self):
        self.label= tk.Label(self.root, text="即時股票資訊", font=("Arial", 20, "bold"))
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
        #抓取stock_listbox的選取事件
        self.stock_listbox.bind('<<ListboxSelect>>', self.on_stock_select)
        
        # 用一個 list 存原始股票資料，避免名稱有 '-' 造成 split 問題
        self.stock_display_list = []
        for stock in self.stock_codes:
            display_text = f"{stock['code']} - {stock['name']}"
            self.stock_display_list.append(stock)  # 保留原始 dict
            self.stock_listbox.insert(tk.END, display_text)
            
            
        self.stock_listbox.pack(side=tk.LEFT)
        self.scrollbar.config(command=self.stock_listbox.yview)

        
        # cancel_button,改變寬度和高度
        cancel_button = tk.Button(root_left_frame, text="取消", command=self.clear_selection)
        cancel_button.pack(side=tk.BOTTOM, pady=(0,10), fill=tk.X, expand=True)

        # 建立root_right_frame來包含選取股票的資訊
        root_right_frame = tk.Frame(self.root)
        root_right_frame.pack(side=tk.RIGHT, pady=10,padx=10,fill=tk.BOTH, expand=True)
        # 在右側顯示選取的股票資訊
        # 增加self.selected_button按鈕click功能
        self.selected_button = tk.Button(
            root_right_frame,
            text="選取的股票數量是0筆",
            font=("Arial", 12, "bold"),
            state=tk.DISABLED,
            command=lambda: threading.Thread(target=self.start_crawling, daemon=True).start()
        )
        self.selected_button.pack(pady=(10,0), padx=10, fill=tk.X)

        # 顯示爬蟲結果，並且靠右對齊
        self.result_label = tk.Label(root_right_frame, text="爬蟲結果:", font=("Arial", 12), anchor="w", justify="right")
        self.result_label.pack(pady=10, padx=10, fill=tk.X)


        tree_frame = tk.Frame(root_right_frame)
        tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 建立 Treeview
        self.stock_info_tree = ttk.Treeview(tree_frame, columns=("股票號碼", "股票名稱", "即時價格", "漲跌", "漲跌百分比", "開盤價", "最高價", "最低價"), show="headings", height=10)

        # 設定欄位標題
        self.stock_info_tree.heading("股票號碼", text="股票號碼")
        self.stock_info_tree.heading("股票名稱", text="股票名稱")
        self.stock_info_tree.heading("即時價格", text="即時價格")
        self.stock_info_tree.heading("漲跌", text="漲跌")
        self.stock_info_tree.heading("漲跌百分比", text="漲跌百分比")
        self.stock_info_tree.heading("開盤價", text="開盤價")
        self.stock_info_tree.heading("最高價", text="最高價")
        self.stock_info_tree.heading("最低價", text="最低價")

        # 設定欄位寬度
        self.stock_info_tree.column("股票號碼", width=80, anchor="center")
        self.stock_info_tree.column("股票名稱", width=100, anchor="w")
        self.stock_info_tree.column("即時價格", width=80, anchor="e")
        self.stock_info_tree.column("漲跌", width=70, anchor="e")
        self.stock_info_tree.column("漲跌百分比", width=90, anchor="e")
        self.stock_info_tree.column("開盤價", width=70, anchor="e")
        self.stock_info_tree.column("最高價", width=70, anchor="e")
        self.stock_info_tree.column("最低價", width=70, anchor="e")

        # 建立垂直滾動條
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.stock_info_tree.yview)
        self.stock_info_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 包裝 treeview 和 scrollbar
        self.stock_info_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        # 當 self.start_crawling 被呼叫時，爬蟲的結果會顯示在這個 Treeview 中

        



    def on_stock_select(self, event=None):
        """當股票被選取時，更新右側顯示的資訊"""
        # 直接用 index 取得原始 dict
        self.selected_stocks = [self.stock_display_list[i] for i in self.stock_listbox.curselection()]
        self.selected_button.config(text=f"選取的股票數量是:{len(self.selected_stocks)}筆")
        if len(self.selected_stocks) == 0:
            self.selected_button.config(state=tk.DISABLED)
        else:
            self.selected_button.config(state=tk.NORMAL)
    def start_crawling(self, event=None):
        """開始爬蟲"""
        self.selected_button.config(state=tk.DISABLED)
        # 清空現有的資料
        for item in self.stock_info_tree.get_children():
            self.stock_info_tree.delete(item)
        
        try:
            # 在這裡可以加入爬蟲邏輯
            # 例如: wantgoo.crawl_stocks(self.selected_stocks)
            urls: list[str] = []
            for stock in self.selected_stocks:
                code = stock['code']
                url_template = f'https://www.wantgoo.com/stock/{code}/technical-chart'
                urls.append(url_template)
            result:list[dict] = asyncio.run(wantgoo.get_stock_data(urls))
            print(f"爬取到的股票資料: {result}")
            
            # 將結果顯示到 Treeview 中
            if result:
                for stock_data in result:
                    if isinstance(stock_data, dict):
                        self.stock_info_tree.insert("", "end", values=(
                            stock_data.get('股票號碼', ''),
                            stock_data.get('股票名稱', ''),
                            stock_data.get('即時價格', ''),
                            stock_data.get('漲跌', ''),
                            stock_data.get('漲跌百分比', ''),
                            stock_data.get('開盤價', ''),
                            stock_data.get('最高價', ''),
                            stock_data.get('最低價', '')
                        ))
        except Exception as e:
            print(f"爬蟲過程中發生錯誤: {e}")
        finally:
            self.selected_button.config(state=tk.NORMAL)

    def clear_selection(self):
        """清除選取的股票"""
        self.stock_listbox.selection_clear(0, tk.END)
        self.selected_stocks = []
        self.selected_button.config(text="選取的股票數量是0筆", state=tk.DISABLED)



if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()