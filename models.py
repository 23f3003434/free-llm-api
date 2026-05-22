import asyncio
from typing import List, Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from app_modules.chat_service import init_browser_instance, run_transaction_on_page

class ScrapeChatModel(BaseChatModel):
    model_name: str = "chatgpt-browser"
    headless: bool = False 
    viewport: dict = {"width": 600, "height": 600}

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Tie tracking states explicitly to THIS object instance
        object.__setattr__(self, "_pw", None)
        object.__setattr__(self, "_browser", None)
        object.__setattr__(self, "_page_object", None)

    async def ensure_browser_initialized(self):
        """Ensures this instance has exactly ONE dedicated browser state running."""
        if getattr(self, "_page_object", None) is None:
            pw, browser, page_object = await init_browser_instance(
                headless=self.headless, 
                viewport=self.viewport
            )
            object.__setattr__(self, "_pw", pw)
            object.__setattr__(self, "_browser", browser)
            object.__setattr__(self, "_page_object", page_object)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        await self.ensure_browser_initialized()
        last_message_text = messages[-1].content
        
        # Pass the unique page object instance to execute the run
        response_text = await run_transaction_on_page(self._page_object, last_message_text)
        
        ai_message = AIMessage(
            content=response_text,
            response_metadata={"model_name": self.model_name, "source": "playwright_scraper"}
        )
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Synchronous fallback executor patched for Jupyter active loops."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._agenerate(messages, stop, run_manager, **kwargs))
        
        if loop.is_running():
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                raise ImportError("Please install nest_asyncio via: pip install nest_asyncio")
        return loop.run_until_complete(self._agenerate(messages, stop, run_manager, **kwargs))

    async def aclose(self):
        """Clean teardown hook that closes ONLY this instance's browser session."""
        browser = getattr(self, "_browser", None)
        pw = getattr(self, "_pw", None)
        
        if browser:
            await browser.close()
            object.__setattr__(self, "_browser", None)
        if pw:
            await pw.stop()
            object.__setattr__(self, "_pw", None)
        object.__setattr__(self, "_page_object", None)

    @property
    def _llm_type(self) -> str:
        return "browser_chat_scraper"
