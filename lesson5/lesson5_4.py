import asyncio
from crawl4ai import (AsyncWebCrawler,
                      CrawlerRunConfig,
                      DefaultMarkdownGenerator,
                      PruningContentFilter)

async def main():
    #建立爬蟲執行的設定配置
    run_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter = PruningContentFilter(
                threshold = 0.6,  # 提高閾值，更嚴格的過濾
                threshold_type = "fixed",
                min_word_threshold = 50  # 最少字數要求
            )
        ),
        # 移除不必要的元素
        excluded_tags=['nav', 'footer', 'header', 'aside', 'form'],
        # 專門針對文章內容的CSS選擇器（可選）
        css_selector='article, .content, .post-content, .entry-content, main'
    )

    #建立一個AsyncWebCrawler的實體
    async with AsyncWebCrawler() as crawler:
        #Run the crawler on a URL
        url = 'https://blockcast.it/2025/07/21/eths-most-hated-rally-could-trigger-331m-in-liquidations/'
        result = await crawler.arun(
                                    url=url,
                                    config=run_config
                                    )
        print(type(result))
        print("=" * 20)        

        #列印取出的結果
        
        print(result.markdown)
        

if __name__ == "__main__":
    asyncio.run(main())
