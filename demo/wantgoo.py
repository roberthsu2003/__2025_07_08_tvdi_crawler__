import asyncio
import json
import twstock

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    JsonCssExtractionStrategy,
    SemaphoreDispatcher,
    RateLimiter,
)

async def get_stock_data(urls: list[str]) -> list[dict]:
    """
    (舊版) 非同步地從 wantgoo.com 抓取股票資料。
    注意：此版本可能會被網站的反爬蟲機制阻擋。
    """
    browser_config = BrowserConfig(
        headless=False,  # 開啟實體瀏覽器以模仿真人
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    
    # 這是針對 wantgoo.com 的第二版 CSS 選擇器
    stock_schema = {
        "name": "StockInfo",
        "baseSelector": "body",
        "fields": [
            {"name": "日期時間", "selector": "#lastQuoteTime", "type": "text"},
            {"name": "股票號碼", "selector": "main header h2 span.code", "type": "text"},
            {"name": "股票名稱", "selector": "main header h2 a", "type": "text"},
            {"name": "即時價格", "selector": "#trade-info .price", "type": "text"},
            {"name": "漲跌", "selector": "#trade-info .change", "type": "text"},
            {"name": "漲跌百分比", "selector": "#trade-info .change-rate", "type": "text"},
            {"name": "開盤價", "selector": "#trade-info .open", "type": "text"},
            {"name": "最高價", "selector": "#trade-info .high", "type": "text"},
            {"name": "成交量(張)", "selector": "#trade-info .volume", "type": "text"},
            {"name": "最低價", "selector": "#trade-info .low", "type": "text"},
            {"name": "前一日收盤價", "selector": "#trade-info .yesterday", "type": "text"},
        ]
    }

    run_config = CrawlerRunConfig(
        wait_for_images=True,
        scan_full_page=True,
        scroll_delay=0.5,
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(stock_schema),
        verbose=True
    )

    dispatcher = SemaphoreDispatcher(
        semaphore_count=5,
        rate_limiter=RateLimiter(base_delay=(0.5, 1.0), max_delay=10.0)
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher,
        )
    
    all_results: list[dict] = []
    for result in results:
        try:
            stack_data: list[dict] = json.loads(result.extracted_content)
            if stack_data:
                all_results.append(stack_data[0])
        except (json.JSONDecodeError, IndexError):
            print(f"無法解析或處理來自 {result.url} 的資料")
            continue

    return all_results

def get_stocks_with_twstock() -> list[dict]:
    """
    從 twstock 套件取得所有上市/上櫃公司清單。
    """
    stocks = twstock.codes
    stock_list = [
        {
            'code': code,
            'name': info.name,
            'market': info.market,
            'group': info.group
        }
        for code, info in stocks.items()
        if info.type == '股票' and len(code) == 4
    ]
    return stock_list