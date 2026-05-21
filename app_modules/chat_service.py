import sys
import time
from playwright.sync_api import sync_playwright
from app_modules.chatgpt_page import ChatGPTPage

_pw_instance = None
_browser_instance = None
_shared_page_object = None

def check_for_active_popups(page) -> bool:
    """
    Active Detection: Instantly scans the DOM for common blocking overlays.
    Returns True if a popup layout is visible.
    """
    popup_identifiers = [
        "div[role='dialog']",
        "div[class*='modal']",
        "text=Terms of use",
        "text=Try the mobile app",
        "button[aria-label='Close']"
    ]
    
    for selector in popup_identifiers:
        try:
            locator = page.locator(selector)
            if locator.is_visible():
                print(f"[🔍 DETECTED] Interface overlay matched: '{selector}'")
                return True
        except Exception:
            pass
            
    return False

def init_browser(headless: bool, viewport: dict):
    """Launches the shared browser instance using the model configurations."""
    global _pw_instance, _browser_instance, _shared_page_object
    
    _pw_instance = sync_playwright().start()
    _browser_instance = _pw_instance.chromium.launch(
        headless=headless,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = _browser_instance.new_context(viewport=viewport)
    page = context.new_page()
    page.goto("https://chatgpt.com")
    
    _shared_page_object = ChatGPTPage(page)

def close_browser():
    """Teardown browser connections cleanly."""
    global _pw_instance, _browser_instance
    if _browser_instance:
        _browser_instance.close()
    if _pw_instance:
        _pw_instance.stop()

def run_transaction(user_message: str) -> str:
    """
    Persistent automation execution loop.
    Intercepts failures and loops indefinitely until the transaction clears.
    """
    global _shared_page_object
    if not _shared_page_object:
        return "Error: Browser service is not active."
        
    # Infinite recovery loop keeps your script running
    while True:
        # Check for popups right away before interacting
        if check_for_active_popups(_shared_page_object.page):
            print("\n" + "="*60)
            print("[⚠️ GUI INTERCEPTED]: A popup is actively blocking the page view.")
            print("[!] RECOVERY ACTION: Manually dismiss the popup in Chrome.")
            print("="*60 + "\n")
            
            # This halts Python execution without dropping the script or closing Chrome
            input("👉 Press [ENTER] inside this terminal once you have cleared the popup to retry... ")
            continue # Goes straight back to the top of the loop to check again

        try:
            # Attempt normal transaction execution
            _shared_page_object.prepare_and_type_prompt(user_message)
            target_index = _shared_page_object.get_assistant_turn_count()
            _shared_page_object.click_send()
            
            # If successful, returns out of the loop cleanly
            return _shared_page_object.wait_and_extract_response(target_index)
            
        except Exception as e:
            print(f"\n[⚠️ EXCEPTION INTERCEPTED]: {type(e).__name__}")
            print("[!] Something blocked element interaction mid-execution.")
            
            # Wait for user validation before retrying the payload cycle
            input("👉 Reset the browser state manually, then press [ENTER] to retry transaction... ")
