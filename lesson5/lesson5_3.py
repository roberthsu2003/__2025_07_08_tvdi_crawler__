import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    #建立一個AsyncWebCrawler的實體
    async with AsyncWebCrawler() as crawler:
        #Run the crawler on a URL
        url = 'https://blockcast.it/2025/07/21/eths-most-hated-rally-could-trigger-331m-in-liquidations/'
        result = await crawler.arun(url=url)
        print(type(result))
        print("=" * 20)        

        #列印取出的結果
        
        print(result.markdown)
        

if __name__ == "__main__":
    asyncio.run(main())
