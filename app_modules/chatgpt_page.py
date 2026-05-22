import asyncio
from playwright.async_api import Page

class ChatGPTPage:
    def __init__(self, page: Page):
        self.page = page
        # Using resilient relative CSS selectors instead of fragile absolute xpaths
        self._input_locator = "div[id='prompt-textarea']"
        self._send_button_testid = "send-button"
        self._inner_markdown = 'div[data-message-author-role="assistant"] div.markdown'

    async def prepare_and_type_prompt(self, prompt_text: str):
        text_field = self.page.locator(self._input_locator).first
        await text_field.wait_for(state="visible", timeout=1000)
        await text_field.click()
        # Ensure field is clear before typing
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Backspace")
        await text_field.fill(prompt_text)

    async def get_assistant_turn_count(self) -> int:
        return await self.page.locator(self._inner_markdown).count()

    async def click_send(self):
        send_button = self.page.get_by_test_id(self._send_button_testid)
        await send_button.wait_for(state="visible", timeout=1000)
        await send_button.click()

    async def wait_and_extract_response(self, target_index: int) -> str:
        """Waits for the new streaming message to finish and extracts text."""
        response_locator = self.page.locator(self._inner_markdown).nth(target_index)
        await response_locator.wait_for(state="visible", timeout=60000)
        
        # Monitor streaming stability (loops until text length stops growing)
        previous_text = ""
        while True:
            await asyncio.sleep(1.0)
            current_text = await response_locator.inner_text()
            if current_text == previous_text and len(current_text) > 0:
                break
            previous_text = current_text
            
        return current_text
