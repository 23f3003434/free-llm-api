from typing import Dict, Any, Optional
from langchain_core.language_models.llms import LLM
from app_modules.chat_service import init_browser, run_transaction, close_browser

class ScrapeLLM(LLM):
    model_name: str = "chatgpt-browser"
    headless: bool = False 
    viewport: Dict[str, int] = {"width": 400, "height": 600}
    

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Delegate setup entirely to the service layer
        init_browser(headless=self.headless, viewport=self.viewport)

    def _call(self, prompt: str, stop: Optional[list[str]] = None, **kwargs: Any) -> str:
        """Simply calls the external function to get the string response."""
        return run_transaction(prompt)

    def __del__(self):
        """Triggers teardown when the script or notebook kernel finishes."""
        close_browser()

    @property
    def _llm_type(self) -> str:
        return "browser_scraper"

# --- Run Test ---
if __name__ == "__main__":
    model = ScrapeLLM()
    print(model.invoke("Tell me a story of a rabbit in 50 words"))
