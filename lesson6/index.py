import wantgoo
import asyncio
import twstock

def get_stocks_with_twstock():
    # 取得所有股票清單
    stocks = twstock.codes
    
    stock_list = []
    for code, info in stocks.items():
        stock_list.append({
            'code': code,
            'name': info.name,
            'market': info.market,
            'group': info.group
        })
    
    return stock_list

def main():
    urls = [
        "https://www.wantgoo.com/stock/2330/technical-chart",
        "https://www.wantgoo.com/stock/2317/technical-chart",
        "https://www.wantgoo.com/stock/2454/technical-chart",
        "https://www.wantgoo.com/stock/2303/technical-chart",
        "https://www.wantgoo.com/stock/2412/technical-chart",
        "https://www.wantgoo.com/stock/2884/technical-chart",
        "https://www.wantgoo.com/stock/2881/technical-chart",
        "https://www.wantgoo.com/stock/2308/technical-chart",
        "https://www.wantgoo.com/stock/2337/technical-chart",
        "https://www.wantgoo.com/stock/2882/technical-chart",
    ]
    reuslts:list[dict] = asyncio.run(wantgoo.get_stock_data(urls=urls))
    for stock in reuslts:
        print(stock)



if __name__ == "__main__":
    #main()
    for item in get_stocks_with_twstock():
        # 只找尋股票代碼第1位數為2的股票,只要4個字元
        if item['code'].startswith('2') and len(item['code']) == 4:
            print(f"股票代碼: {item['code']}, 股票名稱: {item['name']}, 市場: {item['market']}, 分類: {item['group']}")
        