import asyncio
from playwright.async_api import async_playwright
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def scrape(self):
        pass

    async def get_page_content(self, url: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            await browser.close()
            return content
