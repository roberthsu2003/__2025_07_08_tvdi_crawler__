from playwright.async_api import async_playwright
import asyncio


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,slow_mo=1000)
        page = await browser.new_page()
        await page.goto('https://example.com')
        await page.wait_for_selector('p') #等待元素載入
        content = await page.inner_text('p')
        print(content)
        await browser.close()
    
asyncio.run(main())