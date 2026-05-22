import asyncio
import sys
from playwright.async_api import async_playwright, Page, Browser, Playwright
from app_modules.chatgpt_page import ChatGPTPage

async def async_input(prompt: str) -> str:
    """
    Hybrid non-blocking input wrapper.
    Uses Jupyter's interactive input box inside notebooks, 
    and standard async thread read lines inside the terminal.
    """
    is_notebook = 'ipykernel' in sys.modules
    if is_notebook:
        print(prompt, end="", flush=True)
        return await asyncio.to_thread(input)
    else:
        print(prompt, end="", flush=True)
        return await asyncio.to_thread(sys.stdin.readline)

async def check_for_active_popups(page: Page) -> bool:
    """
    Smarter Active Detection: Checks for strict visual roadblocks, 
    CSS blurred/disabled states, and interaction-blocking overlays.
    """
    blocking_text_markers = [
        "terms of use",
        "try the mobile app",
        "verify you are human",
        "stay logged in",
        "welcome back"
    ]
    try:
        # 1. Target structural overlays ONLY if they are visually rendering to the user
        dialog_locator = page.locator("div[role='dialog'], div[class*='modal']").first
        if await dialog_locator.is_visible():
            box = await dialog_locator.bounding_box()
            # Ensure it actually has physical screen real estate
            if box and box['width'] >= 100 and box['height'] >= 100:
                inner_text = await dialog_locator.inner_text()
                # ONLY trigger if the blocking text is actually VISIBLE text inside the modal
                if any(marker in inner_text.lower() for marker in blocking_text_markers):
                    print(f"[🔍 DETECTED] True blocking modal found matching a marker.")
                    return True

        # 2. Advanced Interception Check: Is the primary input box obscured or blurred?
        input_container = page.locator("div[id='prompt-textarea']").first
        
        if await input_container.is_visible():
            # Check if computed styles have locked pointer events or blurred the view
            is_blocked_by_css = await input_container.evaluate("""(element) => {
                const style = window.getComputedStyle(element);
                const bodyStyle = window.getComputedStyle(document.body);
                const mainApp = element.closest('main') || document.body;
                const mainStyle = window.getComputedStyle(mainApp);
                
                return (
                    style.pointerEvents === 'none' || 
                    mainStyle.pointerEvents === 'none' ||
                    mainStyle.filter.includes('blur') ||
                    (bodyStyle.overflow === 'hidden' && document.querySelector('div[role="dialog"]'))
                );
            }""")
            
            if is_blocked_by_css:
                print("[🔍 DETECTED] UI is blurred or disabled via background pointer-events.")
                return True

            # FIX: Removed the trial=True click dry run. 
            # ChatGPT leaves ghost elements in the DOM that fail hit-tests even when the UI is clear.

    except Exception:
        pass
    return False



async def init_browser_instance(headless: bool, viewport: dict) -> tuple[Playwright, Browser, ChatGPTPage]:
    """Launches a standalone browser context and returns its session objects."""
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=headless,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = await browser.new_context(viewport=viewport)
    page = await context.new_page()
    await page.goto("https://chatgpt.com")
    
    page_object = ChatGPTPage(page)
    return pw, browser, page_object

async def run_transaction_on_page(page_object: ChatGPTPage, user_message: str) -> str:
    """Persistent automation loop locked to an explicit page instance."""
    while True:
        if await check_for_active_popups(page_object.page):
            print("\n" + "="*60)
            print("[⚠️ GUI INTERCEPTED]: A popup is actively blocking the page view.")
            print("[!] RECOVERY ACTION: Manually dismiss the popup in Chrome.")
            print("="*60 + "\n")
            await async_input("👉 Press [ENTER] inside this terminal once you have cleared the popup to retry... ")
            continue

        try:
            await page_object.prepare_and_type_prompt(user_message)
            target_index = await page_object.get_assistant_turn_count()
            await page_object.click_send()
            return await page_object.wait_and_extract_response(target_index)
        except Exception as e:
            print(f"\n[⚠️ EXCEPTION INTERCEPTED]: {type(e).__name__}")
            print("[!] Something blocked element interaction mid-execution.")
            await async_input("👉 Reset the browser state manually, then press [ENTER] to retry transaction... ")
