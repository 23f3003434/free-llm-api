import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from app_modules.chatgpt_page import ChatGPTPage
from app_modules.chat_service import execute_chat_transaction

# Global runtime containers for shared state
browser_context = None
shared_page_object = None
playwright_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the startup initialization and shutdown closure of the browser context."""
    global browser_context, shared_page_object, playwright_manager
    
    print("[FastAPI Startup] Initiating automated stealth profile session...")
    playwright_manager = await async_playwright().start()
    user_data_dir = os.path.abspath("./playwright_user_data")
    
    browser_context = await playwright_manager.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    
    page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
    await page.goto("https://chatgpt.com")
    
    # Instantiate layout wrapper
    shared_page_object = ChatGPTPage(page)
    print("[FastAPI Startup] Browser ready for incoming payload transactions.")
    
    yield  # Runs application requests
    
    print("[FastAPI Shutdown] Tearing down resources...")
    await browser_context.close()
    await playwright_manager.stop()

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def process_chat_endpoint(payload: ChatRequest):
    """Receives JSON string text, triggers browser interaction, returns pure string text."""
    if not shared_page_object:
        raise HTTPException(status_code=503, detail="Browser environment is not initialized yet.")
    
    try:
        # Calls the core logic service completely decoupled from the web app
        ai_response_text = await execute_chat_transaction(shared_page_object, payload.message)
        return ChatResponse(response=ai_response_text)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(error)}")

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
