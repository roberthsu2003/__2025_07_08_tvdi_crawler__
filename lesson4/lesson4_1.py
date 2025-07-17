import json
import argparse

class Site:
    def __init__(self,
                 sitename,
                 county,
                 aqi,
                 pollutant,
                 status,
                 pm2_5,
                 pm2_5_avg,
                 latitude,
                 longitude,
                 datacreationdate):      
        # 初始化站點物件的屬性
        self.sitename = sitename          # 站點名稱
        self.county = county              # 所在縣市
        self.aqi = aqi                    # 空氣品質指數
        self.pollutant = pollutant        # 主要污染物
        self.status = status              # 狀態
        self.pm2_5 = pm2_5                # PM2.5 濃度
        self.pm2_5_avg = pm2_5_avg        # PM2.5 平均濃度
        self.latitude = latitude          # 緯度
        self.longitude = longitude        # 經度
        self.datacreationdate = datacreationdate  # 資料建立日期

def parse_sites_from_json(json_file:str)-> list[Site]:
    # 從JSON檔案解析站點資料
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    site_list = []
    for sitename in data['records']:
        # 為每個站點建立Site物件
        site = Site(
            sitename=sitename['sitename'],           # 站點名稱
            county=sitename['county'],               # 所在縣市
            aqi=sitename['aqi'],                     # 空氣品質指數
            pollutant=sitename['pollutant'],         # 主要污染物
            status=sitename['status'],               # 狀態
            pm2_5=sitename['pm2.5'],                 # PM2.5 濃度
            pm2_5_avg=sitename['pm2.5_avg'],         # PM2.5 平均濃度
            latitude=sitename['latitude'],           # 緯度
            longitude=sitename['longitude'],         # 經度
            datacreationdate=sitename['datacreationdate']  # 資料建立日期
        )
        site_list.append(site)
    return site_list


if __name__ == '__main__':
    # 設定命令列參數解析
    parser = argparse.ArgumentParser(description='AQI 資料查詢 CLI')
    # 新增縣市過濾參數，可使用 -c 或 --county 或 --country 指定縣市名稱
    parser.add_argument('-c', '--county', dest='county', help='過濾縣市名稱 (例如: 臺北市、高雄市)', default=None)
    # 新增檔案路徑參數，可使用 --file 或 -f 指定 JSON 檔案路徑
    parser.add_argument('--file', '-f', help='JSON 檔案路徑 (預設: aqx_p_488.json)', default='aqx_p_488.json')
    # 解析命令列參數
    args = parser.parse_args()

    # 解析JSON檔案中的站點資料
    parsed_sites:list[Site] = parse_sites_from_json(args.file)
    # 如果指定了縣市，則過濾出該縣市的站點
    if args.county:
        parsed_sites = [s for s in parsed_sites if s.county == args.county]
    # 顯示每個站點的資訊
    for site in parsed_sites:
        print(f"站點名稱: {site.sitename}, 所在縣市: {site.county}, AQI: {site.aqi}, 主要污染物: {site.pollutant}")
    
