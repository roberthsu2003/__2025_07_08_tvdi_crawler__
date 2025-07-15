import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os

class Site:
    def __init__(self, sitename, county, aqi, pollutant, status, pm2_5, pm2_5_avg, latitude, longitude, datacreationdate):
        self.sitename = sitename
        self.county = county
        self.aqi = aqi
        self.pollutant = pollutant
        self.status = status
        self.pm2_5 = pm2_5
        self.pm2_5_avg = pm2_5_avg
        self.latitude = latitude
        self.longitude = longitude
        self.datacreationdate = datacreationdate

class AQIViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("AQI 空氣品質監測站查詢系統")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 設定樣式
        self.setup_styles()
        
        # 資料儲存
        self.all_sites = []
        self.filtered_sites = []
        
        # 建立介面
        self.create_widgets()
        
        # 預設載入檔案
        self.load_default_file()
    
    def setup_styles(self):
        """設定 ttk 樣式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 設定按鈕樣式
        style.configure('Custom.TButton', 
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        # 設定標籤樣式
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       background='#f0f0f0',
                       foreground='#2c3e50')
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#f0f0f0',
                       foreground='#34495e')
    
    def create_widgets(self):
        """建立所有 GUI 元件"""
        # 主標題
        title_frame = tk.Frame(self.root, bg='#f0f0f0', pady=20)
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(title_frame, text="🌬️ AQI 空氣品質監測站查詢系統", 
                               style='Title.TLabel')
        title_label.pack()
        
        # 控制面板
        control_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        control_frame.pack(fill='x', padx=20)
        
        # 檔案選擇區域
        file_frame = tk.Frame(control_frame, bg='#f0f0f0')
        file_frame.pack(fill='x', pady=5)
        
        ttk.Label(file_frame, text="📁 資料檔案:", style='Header.TLabel').pack(side='left')
        
        self.file_var = tk.StringVar(value="aqx_p_488.json")
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        file_entry.pack(side='left', padx=(10, 5))
        
        ttk.Button(file_frame, text="瀏覽", command=self.browse_file,
                  style='Custom.TButton').pack(side='left', padx=5)
        
        ttk.Button(file_frame, text="載入資料", command=self.load_data,
                  style='Custom.TButton').pack(side='left', padx=5)
        
        # 篩選區域
        filter_frame = tk.Frame(control_frame, bg='#f0f0f0')
        filter_frame.pack(fill='x', pady=10)
        
        ttk.Label(filter_frame, text="🏙️ 縣市篩選:", style='Header.TLabel').pack(side='left')
        
        self.county_var = tk.StringVar()
        self.county_combo = ttk.Combobox(filter_frame, textvariable=self.county_var, 
                                        width=20, state='readonly')
        self.county_combo.pack(side='left', padx=(10, 5))
        self.county_combo.bind('<<ComboboxSelected>>', self.filter_data)
        
        ttk.Button(filter_frame, text="顯示全部", command=self.show_all,
                  style='Custom.TButton').pack(side='left', padx=5)
        
        # 統計資訊區域
        stats_frame = tk.Frame(control_frame, bg='#f0f0f0')
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="📊 載入資料後顯示統計資訊", 
                                    style='Header.TLabel')
        self.stats_label.pack(side='left')
        
        # 資料顯示區域
        data_frame = tk.Frame(self.root, bg='#f0f0f0')
        data_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 建立 Treeview
        columns = ('站點名稱', '縣市', 'AQI', '主要污染物', '狀態', 'PM2.5', 'PM2.5平均')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題和寬度
        column_widths = [120, 80, 60, 100, 80, 80, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        # 加入滾動條
        scrollbar_y = ttk.Scrollbar(data_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(data_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 佈局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)
        
        # 詳細資訊區域
        detail_frame = tk.Frame(self.root, bg='#f0f0f0')
        detail_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(detail_frame, text="📋 詳細資訊 (點擊站點查看):", 
                 style='Header.TLabel').pack(anchor='w')
        
        self.detail_text = ScrolledText(detail_frame, height=6, wrap='word',
                                       font=('Consolas', 10))
        self.detail_text.pack(fill='x', pady=5)
        
        # 綁定選擇事件
        self.tree.bind('<<TreeviewSelect>>', self.show_detail)
    
    def browse_file(self):
        """瀏覽檔案"""
        filename = filedialog.askopenfilename(
            title="選擇 JSON 檔案",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.file_var.set(filename)
    
    def load_default_file(self):
        """載入預設檔案"""
        if os.path.exists("aqx_p_488.json"):
            self.load_data()
    
    def load_data(self):
        """載入資料"""
        try:
            filename = self.file_var.get()
            if not os.path.exists(filename):
                messagebox.showerror("錯誤", f"檔案不存在: {filename}")
                return
            
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.all_sites = []
            for record in data['records']:
                site = Site(
                    sitename=record['sitename'],
                    county=record['county'],
                    aqi=record['aqi'],
                    pollutant=record['pollutant'],
                    status=record['status'],
                    pm2_5=record['pm2.5'],
                    pm2_5_avg=record['pm2.5_avg'],
                    latitude=record['latitude'],
                    longitude=record['longitude'],
                    datacreationdate=record['datacreationdate']
                )
                self.all_sites.append(site)
            
            self.filtered_sites = self.all_sites.copy()
            self.update_county_combo()
            self.update_display()
            self.update_stats()
            
            messagebox.showinfo("成功", f"成功載入 {len(self.all_sites)} 筆資料")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入檔案時發生錯誤:\n{str(e)}")
    
    def update_county_combo(self):
        """更新縣市下拉選單"""
        counties = sorted(set(site.county for site in self.all_sites))
        self.county_combo['values'] = ['全部'] + counties
        self.county_combo.set('全部')
    
    def filter_data(self, event=None):
        """篩選資料"""
        selected_county = self.county_var.get()
        if selected_county == '全部' or not selected_county:
            self.filtered_sites = self.all_sites.copy()
        else:
            self.filtered_sites = [site for site in self.all_sites 
                                 if site.county == selected_county]
        
        self.update_display()
        self.update_stats()
    
    def show_all(self):
        """顯示全部資料"""
        self.county_combo.set('全部')
        self.filtered_sites = self.all_sites.copy()
        self.update_display()
        self.update_stats()
    
    def update_display(self):
        """更新顯示"""
        # 清空現有資料
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 加入新資料
        for site in self.filtered_sites:
            self.tree.insert('', 'end', values=(
                site.sitename,
                site.county,
                site.aqi,
                site.pollutant,
                site.status,
                site.pm2_5,
                site.pm2_5_avg
            ))
    
    def update_stats(self):
        """更新統計資訊"""
        if not self.filtered_sites:
            self.stats_label.config(text="📊 無資料")
            return
        
        total = len(self.filtered_sites)
        counties = len(set(site.county for site in self.filtered_sites))
        
        # 計算 AQI 統計
        aqi_values = [int(site.aqi) for site in self.filtered_sites if site.aqi.isdigit()]
        if aqi_values:
            avg_aqi = sum(aqi_values) / len(aqi_values)
            max_aqi = max(aqi_values)
            min_aqi = min(aqi_values)
            stats_text = f"📊 總計: {total} 站點 | 縣市: {counties} 個 | AQI 平均: {avg_aqi:.1f} | 最高: {max_aqi} | 最低: {min_aqi}"
        else:
            stats_text = f"📊 總計: {total} 站點 | 縣市: {counties} 個"
        
        self.stats_label.config(text=stats_text)
    
    def show_detail(self, event):
        """顯示詳細資訊"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        sitename = item['values'][0]
        
        # 找到對應的站點
        site = next((s for s in self.filtered_sites if s.sitename == sitename), None)
        if not site:
            return
        
        detail_info = f"""
🏭 站點名稱: {site.sitename}
🏙️ 所在縣市: {site.county}
📊 AQI 指數: {site.aqi}
🌫️ 主要污染物: {site.pollutant}
✅ 監測狀態: {site.status}
🔬 PM2.5 即時: {site.pm2_5}
📈 PM2.5 平均: {site.pm2_5_avg}
📍 經緯度: {site.latitude}, {site.longitude}
📅 資料時間: {site.datacreationdate}
        """.strip()
        
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, detail_info)

def main():
    root = tk.Tk()
    app = AQIViewer(root)
    root.mainloop()

if __name__ == '__main__':
    main()