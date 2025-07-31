import asyncio
import json
import twstock

from crawl4ai import (AsyncWebCrawler,
                      BrowserConfig,
                      CrawlerRunConfig,
                      CacheMode,
                      JsonCssExtractionStrategy,
                      SemaphoreDispatcher,RateLimiter,
                      )

async def get_stock_data(urls:list[str])-> list[dict]:
    """
    非同步地從一組網址列表抓取股票資料，使用無頭的Chromium瀏覽器。

    此函式利用非同步網頁爬蟲，搭配自訂的瀏覽器與執行設定，
    擷取如日期時間、股票代碼、名稱、即時價格、漲跌、漲跌百分比、
    開盤價、最高價、成交量、最低價、前一日收盤價等資訊。
    資料擷取依據 schema 中定義的 CSS 選擇器。

    參數:
        urls (list[str]): 要抓取股票資料的網址列表。

    回傳:
        list[dict]: 每個網址對應一筆擷取到的股票資訊字典。

    備註:
        - 使用 SemaphoreDispatcher 控制並發數量與速率限制。
        - 爬蟲會等待圖片載入、掃描整頁並滾動延遲。
        - 擷取策略採用 JSON-CSS，依據 schema 設定。
    """
   

    browser_config = BrowserConfig(
        headless=True
    )
    stock_schema = {
        "name": "StockInfo",
        "baseSelector": "main.main",  # 從整個頁面開始選擇
        "fields": [
            {
                "name":"日期時間",
                "selector":"time.last-time#lastQuoteTime",
                "type":"text"
            },
            {
                "name": "股票號碼",
                "selector": "span.astock-code[c-model='id']", # 假設股票代碼在這個選擇器下
                "type": "text"
            },
            {
                "name": "股票名稱",
                "selector": "h3.astock-name[c-model='name']",  # 假設股票名稱在這個選擇器下
                "type": "text"
            },
            {
                "name": "即時價格",
                "selector":"div.quotes-info div.deal",
                "type": "text"

            },
            {
                "name": "漲跌",
                "selector":"div.quotes-info span.chg[c-model='change']",
                "type": "text"
            },
            {
                "name": "漲跌百分比",
                "selector":"div.quotes-info span.chg-rate[c-model='changeRate']",
                "type": "text"
            },
            {
                "name": "開盤價",
                "selector":"div.quotes-info #quotesUl span[c-model-dazzle='text:open,class:openUpDn']",
                "type": "text"
            },
            {
                "name": "最高價",
                "selector":"div.quotes-info #quotesUl span[c-model-dazzle='text:high,class:highUpDn']",
                "type": "text"

            },
            {
                "name": "成交量(張)",
                "selector":"div.quotes-info #quotesUl span[c-model='volume']",
                "type": "text" 
            },
            {
                "name": "最低價",
                "selector":"div.quotes-info #quotesUl span[c-model-dazzle='text:low,class:lowUpDn']",
                "type": "text" 
            },
            {
                "name": "前一日收盤價",
                "selector":"div.quotes-info #quotesUl span[c-model='previousClose']",
                "type": "text" 
            }

        ]
    }

    # 建立一個AsyncWebCrawler的實體，並傳入BrowserConfig實體
    
    # 這樣可以讓爬蟲等待瀏覽器載入頁面，並且可以在瀏覽器中看到爬蟲的操作，方便除錯
    run_config = CrawlerRunConfig(
        wait_for_images=True,  # 等待圖片載入
        scan_full_page=True,  # 掃描整個頁面
        scroll_delay=0.5,     # 滾動步驟之間的延遲（秒)
        #想要在`class="my-drawer-toggle-btn"`的元素上點擊
        #js_code=["document.querySelector('.my-drawer-toggle-btn').click();"],
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(stock_schema),
        verbose=True
    )

    dispatcher = SemaphoreDispatcher(
        semaphore_count=5,
        rate_limiter=RateLimiter(
            base_delay=(0.5, 1.0),
            max_delay=10.0
        )
    )

    # 使用AsyncWebCrawler的實體來爬取網頁
    # 加入run_config參數
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher,
            )
    all_results:list[dict] = []
    for result in results:
        stack_data:list[dict] = json.loads(result.extracted_content)
        all_results.append(stack_data[0])

    return all_results


def get_stocks_with_twstock()->list[dict]:
    """
    從 twstock 套件取得所有股票清單，並篩選出股票代碼以 '2' 開頭且長度為 4 的股票。

    回傳:
        list[dict]: 每筆資料包含以下欄位：
            - 'code': 股票代碼 (str)
            - 'name': 股票名稱 (str)
            - 'market': 市場類型 (str)
            - 'group': 產業類別 (str)
    """
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

    return_list = []
    
    for item in stock_list:
        # 只找尋股票代碼第1位數為2的股票,只要4個字元
        if item['code'].startswith('2') and len(item['code']) == 4:
            return_list.append(item)
    return return_list