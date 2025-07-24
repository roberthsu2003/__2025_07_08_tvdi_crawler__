import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    url = 'https://www.wantgoo.com/stock/2330/technical-chart'
    #建立一個BrowserConfig,讓chromium的瀏覽器顯示
    #BrowserConfig實體
    browser_config = BrowserConfig(
        headless=False
    )
    # 建立一個AsyncWebCrawler的實體，並傳入BrowserConfig實體
    # 這樣可以讓爬蟲等待瀏覽器載入頁面，並且可以在瀏覽器中看到爬蟲的操作，方便除錯
    run_config = CrawlerRunConfig(
        wait_for_images=True,  # 等待圖片載入
        scan_full_page=True,  # 掃描整個頁面
        scroll_delay=0.5,     # 滾動步驟之間的延遲（秒)
        #想要在`class="my-drawer-toggle-btn"`的元素上點擊
        #js_code=["document.querySelector('.my-drawer-toggle-btn').click();"],
        cache_mode=CacheMode.BYPASS,
        verbose=True
    )
    # 使用AsyncWebCrawler的實體來爬取網頁
    # 加入run_config參數
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url,config=run_config)
        print(result.markdown) #

if __name__ == '__main__':
    asyncio.run(main())
    