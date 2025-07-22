import json
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_crypto_prices():
    dummy_html = """
    <html>
      <body>
        <div class='crypto-row'>
          <h2 class='coin-name'>Bitcoin</h2>
          <span class='coin-price'>$28,000</span>
        </div>
        <div class='crypto-row'>
          <h2 class='coin-name'>Ethereum</h2>
          <span class='coin-price'>$1,800</span>
        </div>
      </body>
    </html>
    """
    #1. 定義一個簡單的extraction schema
    schema = {
        "name":"Crypto Prices",
        "baseSelector": "div.crypto-row",
        "fields":[
            {
                "name": "coin_name",
                "selector": "h2.coin-name",
                "type":"text"
            },
            {
                "name":"price",
                "selector":"span.coin-price",
                "type":"text"
            }
        ]
    }

    #2. 建立extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True) #Enables verbose logging for debugging purposes.

    #3. 設定爬蟲配置
    config = CrawlerRunConfig(
        cache_mode = CacheMode.BYPASS,
        extraction_strategy=extraction_strategy
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        #4. 執行爬蟲和提取任務
        raw_url = f"raw://{dummy_html}"
        result = await crawler.arun(
            url=raw_url,
            config=config
        )

        if not result.success:
            print("Crawl failed:", result.error_message)
            return
        
        # 5. 解析被提取的json資料
        data = json.loads(result.extracted_content)
        print("====取出的內容========")
        print(data)
        print("\n======取出的筆數=======")
        print(f"Extracted {len(data)} coin entries")
        print("\n第1筆資料")
        print(json.dumps(data[0], indent=2) if data else "No Data found")

asyncio.run(extract_crypto_prices())

