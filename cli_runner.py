import asyncio
from playwright.async_api import async_playwright
from app_modules.chatgpt_page import ChatGPTPage
from app_modules.chat_service import execute_chat_transaction, get_async_stdin_fallback

async def run_standalone_cli():
    async with async_playwright() as p:
        user_data_dir = "./playwright_user_data"
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://chatgpt.com")
        
        chat_page = ChatGPTPage(page)
        print("\n=== Standalone CLI Runner Environment Active ===")
        
        while True:
            user_input = await get_async_stdin_fallback("\n[You]: ")
            user_input = user_input.strip()
            
            if user_input.lower() in ["exit", "quit"]:
                break
                
            # Execute standard core module engine
            print("[CLI] Dispatched payload to core logic engine...")
            response = await execute_chat_transaction(chat_page, user_input)
            print(f"\n[AI Response Output]:\n{response}")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_standalone_cli())
