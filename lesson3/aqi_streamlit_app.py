import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# 設定頁面配置
st.set_page_config(
    page_title="台灣空氣品質監測系統",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .aqi-good { color: #00e400; font-weight: bold; }
    .aqi-moderate { color: #ffff00; font-weight: bold; }
    .aqi-unhealthy-sensitive { color: #ff7e00; font-weight: bold; }
    .aqi-unhealthy { color: #ff0000; font-weight: bold; }
    .aqi-very-unhealthy { color: #8f3f97; font-weight: bold; }
    .aqi-hazardous { color: #7e0023; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

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

@st.cache_data
def load_aqi_data(json_file='aqx_p_488.json'):
    """載入並解析AQI資料"""
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        site_list = []
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
            site_list.append(site)
        return site_list
    except Exception as e:
        st.error(f"載入資料時發生錯誤: {e}")
        return []

def get_aqi_color(aqi_value):
    """根據AQI值返回對應的顏色和狀態"""
    try:
        aqi = int(aqi_value) if aqi_value and aqi_value != '' else 0
    except:
        return "#cccccc", "無資料"
    
    if aqi <= 50:
        return "#00e400", "良好"
    elif aqi <= 100:
        return "#ffff00", "普通"
    elif aqi <= 150:
        return "#ff7e00", "對敏感族群不健康"
    elif aqi <= 200:
        return "#ff0000", "對所有族群不健康"
    elif aqi <= 300:
        return "#8f3f97", "非常不健康"
    else:
        return "#7e0023", "危險"

def create_dataframe(sites):
    """將Site物件轉換為DataFrame"""
    data = []
    for site in sites:
        data.append({
            '測站名稱': site.sitename,
            '縣市': site.county,
            'AQI': site.aqi,
            '主要污染物': site.pollutant,
            '狀態': site.status,
            'PM2.5': site.pm2_5,
            'PM2.5平均': site.pm2_5_avg,
            '緯度': site.latitude,
            '經度': site.longitude,
            '資料建立時間': site.datacreationdate
        })
    return pd.DataFrame(data)

def main():
    # 主標題
    st.markdown('<h1 class="main-header">🌬️ 台灣空氣品質監測系統</h1>', unsafe_allow_html=True)
    
    # 載入資料
    sites = load_aqi_data()
    if not sites:
        st.error("無法載入資料，請檢查資料檔案是否存在。")
        return
    
    df = create_dataframe(sites)
    
    # 側邊欄篩選器
    st.sidebar.header("🔍 資料篩選")
    
    # 縣市篩選
    counties = sorted(df['縣市'].unique())
    selected_counties = st.sidebar.multiselect(
        "選擇縣市",
        counties,
        default=counties[:5] if len(counties) > 5 else counties
    )
    
    # AQI範圍篩選
    aqi_values = []
    for aqi in df['AQI']:
        try:
            if aqi and aqi != '':
                aqi_values.append(int(aqi))
        except:
            continue
    
    if aqi_values:
        min_aqi, max_aqi = st.sidebar.slider(
            "AQI 範圍",
            min_value=min(aqi_values),
            max_value=max(aqi_values),
            value=(min(aqi_values), max(aqi_values))
        )
    else:
        min_aqi, max_aqi = 0, 500
    
    # 篩選資料
    filtered_df = df[df['縣市'].isin(selected_counties)]
    
    # AQI篩選
    def filter_aqi(row):
        try:
            aqi = int(row['AQI']) if row['AQI'] and row['AQI'] != '' else 0
            return min_aqi <= aqi <= max_aqi
        except:
            return False
    
    filtered_df = filtered_df[filtered_df.apply(filter_aqi, axis=1)]
    
    # 主要指標
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總測站數", len(df))
    
    with col2:
        st.metric("篩選後測站數", len(filtered_df))
    
    with col3:
        valid_aqi = [int(aqi) for aqi in filtered_df['AQI'] if aqi and aqi != '' and str(aqi).isdigit()]
        avg_aqi = np.mean(valid_aqi) if valid_aqi else 0
        st.metric("平均 AQI", f"{avg_aqi:.1f}")
    
    with col4:
        counties_count = len(filtered_df['縣市'].unique())
        st.metric("涵蓋縣市數", counties_count)
    
    # 主要內容區域
    tab1, tab2, tab3, tab4 = st.tabs(["📊 總覽", "🗺️ 地圖", "📈 統計圖表", "📋 詳細資料"])
    
    with tab1:
        st.subheader("空氣品質總覽")
        
        # AQI分布統計
        aqi_stats = {}
        for _, row in filtered_df.iterrows():
            try:
                aqi = int(row['AQI']) if row['AQI'] and row['AQI'] != '' else 0
            except:
                aqi = 0
            
            color, status = get_aqi_color(aqi)
            aqi_stats[status] = aqi_stats.get(status, 0) + 1
        
        # 顯示AQI分布
        cols = st.columns(len(aqi_stats))
        for i, (status, count) in enumerate(aqi_stats.items()):
            with cols[i]:
                st.metric(status, count)
        
        # 最新更新時間
        if not filtered_df.empty:
            latest_time = filtered_df['資料建立時間'].iloc[0]
            st.info(f"📅 資料更新時間: {latest_time}")
    
    with tab2:
        st.subheader("測站分布地圖")
        
        # 準備地圖資料
        map_data = []
        for _, row in filtered_df.iterrows():
            try:
                lat = float(row['緯度']) if row['緯度'] else None
                lon = float(row['經度']) if row['經度'] else None
                aqi = int(row['AQI']) if row['AQI'] and row['AQI'] != '' else 0
                
                if lat and lon:
                    color, status = get_aqi_color(aqi)
                    map_data.append({
                        'lat': lat,
                        'lon': lon,
                        'sitename': row['測站名稱'],
                        'county': row['縣市'],
                        'aqi': aqi,
                        'status': status,
                        'color': color,
                        'pollutant': row['主要污染物']
                    })
            except:
                continue
        
        if map_data:
            map_df = pd.DataFrame(map_data)
            
            # 使用Plotly創建地圖
            fig = px.scatter_mapbox(
                map_df,
                lat="lat",
                lon="lon",
                color="aqi",
                size="aqi",
                hover_name="sitename",
                hover_data={"county": True, "status": True, "pollutant": True},
                color_continuous_scale="RdYlGn_r",
                size_max=15,
                zoom=7,
                height=600
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("沒有有效的地理位置資料可顯示")
    
    with tab3:
        st.subheader("統計圖表")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AQI分布直方圖
            valid_aqi_data = []
            for _, row in filtered_df.iterrows():
                try:
                    aqi = int(row['AQI']) if row['AQI'] and row['AQI'] != '' else 0
                    if aqi > 0:
                        valid_aqi_data.append(aqi)
                except:
                    continue
            
            if valid_aqi_data:
                fig_hist = px.histogram(
                    x=valid_aqi_data,
                    nbins=20,
                    title="AQI 分布直方圖",
                    labels={'x': 'AQI 值', 'y': '測站數量'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # 縣市AQI平均值
            county_aqi = {}
            for _, row in filtered_df.iterrows():
                county = row['縣市']
                try:
                    aqi = int(row['AQI']) if row['AQI'] and row['AQI'] != '' else 0
                    if county not in county_aqi:
                        county_aqi[county] = []
                    if aqi > 0:
                        county_aqi[county].append(aqi)
                except:
                    continue
            
            county_avg = {k: np.mean(v) for k, v in county_aqi.items() if v}
            
            if county_avg:
                fig_bar = px.bar(
                    x=list(county_avg.keys()),
                    y=list(county_avg.values()),
                    title="各縣市平均 AQI",
                    labels={'x': '縣市', 'y': '平均 AQI'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # 污染物分布圓餅圖
        pollutant_counts = filtered_df['主要污染物'].value_counts()
        if not pollutant_counts.empty:
            fig_pie = px.pie(
                values=pollutant_counts.values,
                names=pollutant_counts.index,
                title="主要污染物分布"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab4:
        st.subheader("詳細資料表")
        
        # 搜尋功能
        search_term = st.text_input("🔍 搜尋測站名稱或縣市")
        if search_term:
            mask = (filtered_df['測站名稱'].str.contains(search_term, case=False, na=False) |
                   filtered_df['縣市'].str.contains(search_term, case=False, na=False))
            display_df = filtered_df[mask]
        else:
            display_df = filtered_df
        
        # 排序選項
        sort_column = st.selectbox("排序依據", ['AQI', '測站名稱', '縣市', 'PM2.5'])
        sort_order = st.radio("排序方式", ['升序', '降序'], horizontal=True)
        
        if sort_column == 'AQI':
            # 特殊處理AQI排序
            display_df = display_df.copy()
            display_df['AQI_numeric'] = pd.to_numeric(display_df['AQI'], errors='coerce').fillna(0)
            display_df = display_df.sort_values('AQI_numeric', ascending=(sort_order == '升序'))
            display_df = display_df.drop('AQI_numeric', axis=1)
        else:
            display_df = display_df.sort_values(sort_column, ascending=(sort_order == '升序'))
        
        # 顯示資料表
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # 下載功能
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下載 CSV 檔案",
            data=csv,
            file_name=f"aqi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()