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

        # 新增搜尋功能
        search_frame = tk.Frame(root_left_frame)
        search_frame.pack(pady=(5, 0), padx=10, fill=tk.X)
        
        search_label = tk.Label(search_frame, text="搜尋股票代碼或名稱:", font=("Arial", 10))
        search_label.pack(anchor="w")
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10))
        self.search_entry.pack(fill=tk.X, pady=(2, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # 清除搜尋按鈕
        search_clear_button = tk.Button(search_frame, text="清除搜尋", command=self.clear_search, font=("Arial", 9))
        search_clear_button.pack(pady=(2, 0))

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
        self.selected_button.pack(pady=10, padx=10, fill=tk.X, expand=True)
        
        # 添加 Treeview 來顯示爬蟲結果
        self.create_result_treeview(root_right_frame)
    
    def create_result_treeview(self, parent):
        """建立顯示爬蟲結果的 Treeview"""
        # 標題
        result_title = tk.Label(parent, text="爬蟲結果", font=("Arial", 12, "bold"), anchor="w")
        result_title.pack(pady=(10, 5), fill=tk.X, padx=10)
        
        # 建立 Treeview 框架
        tree_frame = tk.Frame(parent)
        tree_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # 定義 Treeview 欄位
        columns = ("stock_code", "stock_name", "current_price", "change", "change_rate", 
                  "open_price", "high_price", "low_price", "volume", "prev_close", "datetime")
        
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 設定欄位標題和寬度
        column_configs = {
            "stock_code": ("股票代碼", 80),
            "stock_name": ("股票名稱", 100),
            "current_price": ("即時價格", 80),
            "change": ("漲跌", 60),
            "change_rate": ("漲跌%", 70),
            "open_price": ("開盤", 70),
            "high_price": ("最高", 70),
            "low_price": ("最低", 70),
            "volume": ("成交量", 80),
            "prev_close": ("昨收", 70),
            "datetime": ("更新時間", 120)
        }
        
        for col, (heading, width) in column_configs.items():
            self.result_tree.heading(col, text=heading)
            self.result_tree.column(col, width=width, minwidth=50)
        
        # 添加捲軸
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        
        self.result_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 配置 grid
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 添加清除按鈕
        clear_button = tk.Button(parent, text="清除結果", command=self.clear_results)
        clear_button.pack(pady=5, padx=10, fill=tk.X)
    
    def update_treeview_with_results(self, results):
        """更新 Treeview 顯示爬蟲結果"""
        # 清除現有內容
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 添加新結果
        for result in results:
            # 處理資料格式，確保所有欄位都有值
            values = (
                result.get("股票號碼", "N/A"),
                result.get("股票名稱", "N/A"),
                result.get("即時價格", "N/A"),
                result.get("漲跌", "N/A"),
                result.get("漲跌百分比", "N/A"),
                result.get("開盤價", "N/A"),
                result.get("最高價", "N/A"),
                result.get("最低價", "N/A"),
                result.get("成交量(張)", "N/A"),
                result.get("前一日收盤價", "N/A"),
                result.get("日期時間", "N/A")
            )
            
            self.result_tree.insert("", "end", values=values)
    
    def clear_results(self):
        """清除 Treeview 中的結果和左側 listbox 的選取狀態"""
        # 清除 Treeview 結果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 清除搜尋條件
        self.search_entry.delete(0, tk.END)
        
        # 清除選取狀態
        self.selected_stocks = []
        
        # 重新載入所有股票（不保留選取狀態）
        self.on_search()
        
        # 強制清除選取狀態（因為 on_search 可能會嘗試恢復）
        self.stock_listbox.selection_clear(0, tk.END)
        self.selected_stocks = []
        self.update_button_status()
    
    def on_search(self, event=None):
        """搜尋功能：根據輸入的關鍵字過濾股票列表，保留已選取的股票"""
        search_text = self.search_entry.get().lower().strip()
        
        # 保存當前選取的股票代碼
        selected_codes = [stock['code'] for stock in self.selected_stocks] if hasattr(self, 'selected_stocks') else []
        
        # 清除 listbox 現有內容
        self.stock_listbox.delete(0, tk.END)
        
        # 重置顯示列表
        self.stock_display_list = []
        
        # 根據搜尋條件過濾股票
        for stock in self.stock_codes:
            stock_code = stock['code'].lower()
            stock_name = stock['name'].lower()
            
            # 如果搜尋框為空，顯示所有股票
            # 否則檢查股票代碼或名稱是否包含搜尋關鍵字
            if not search_text or search_text in stock_code or search_text in stock_name:
                display_text = f"{stock['code']} - {stock['name']}"
                self.stock_display_list.append(stock)
                self.stock_listbox.insert(tk.END, display_text)
        
        # 恢復之前選取的股票
        self.selected_stocks = []
        for i, stock in enumerate(self.stock_display_list):
            if stock['code'] in selected_codes:
                self.stock_listbox.selection_set(i)
                self.selected_stocks.append(stock)
        
        # 更新按鈕狀態
        self.update_button_status()
    
    def update_button_status(self):
        """更新按鈕狀態和文字"""
        if len(self.selected_stocks) == 0:
            self.selected_button.config(text="選取的股票數量是0筆", state=tk.DISABLED)
        else:
            self.selected_button.config(text=f"選取的股票數量是:{len(self.selected_stocks)}筆", state=tk.NORMAL)
    
    def clear_search(self):
        """清除搜尋條件，恢復顯示所有股票"""
        self.search_entry.delete(0, tk.END)
        self.on_search()  # 觸發搜尋更新，顯示所有股票
    
    def show_loading_status(self, is_loading=True):
        """顯示載入狀態"""
        if is_loading:
            self.selected_button.config(text="正在爬取資料中...", state=tk.DISABLED)
        else:
            self.selected_button.config(text=f"選取的股票數量是:{len(self.selected_stocks)}筆", state=tk.NORMAL)
    
    def on_stock_select(self, event=None):
        """當股票被選取時，更新右側顯示的資訊"""
        # 直接用 index 取得原始 dict
        self.selected_stocks = [self.stock_display_list[i] for i in self.stock_listbox.curselection()]
        self.update_button_status()
    def start_crawling(self, event=None):
        """開始爬蟲"""
        self.show_loading_status(True)
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
            
            # 更新 Treeview 顯示結果
            self.update_treeview_with_results(result)
            
        except Exception as e:
            print(f"爬蟲過程中發生錯誤: {e}")
            # 可以在這裡顯示錯誤訊息給使用者
        finally:
            self.show_loading_status(False)

    def clear_selection(self):
        """清除選取的股票"""
        self.stock_listbox.selection_clear(0, tk.END)
        self.selected_stocks = []
        self.selected_button.config(text="選取的股票數量是0筆", state=tk.DISABLED)



if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()