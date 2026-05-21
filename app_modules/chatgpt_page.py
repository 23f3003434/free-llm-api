import asyncio
from playwright.async_api import Page

class ChatGPTPage:
    """Encapsulates all layout selectors and raw DOM actions for ChatGPT."""
    def __init__(self, page: Page):
        self.page = page
        # Centralized selectors
        self._input_xpath = "xpath=/html/body/div/div/div/div/div/div/main/div/div/div/div/div/div/div/div/div/div/form/div/div/div/div/div/p"
        self._send_button_testid = "send-button"
        self._assistant_sections = 'section[data-turn="assistant"]'
        self._inner_markdown = 'div[data-message-author-role="assistant"] div.markdown'

    async def prepare_and_type_prompt(self, prompt_text: str):
        text_field = self.page.locator(self._input_xpath)
        await text_field.wait_for(state="visible", timeout=3000)
        await text_field.click()
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Backspace")
        await self.page.keyboard.type(prompt_text, delay=15)

    async def get_assistant_turn_count(self) -> int:
        return await self.page.locator(self._assistant_sections).count()

    async def click_send(self):
        send_button = self.page.get_by_test_id(self._send_button_testid)
        await send_button.wait_for(state="visible", timeout=3000)
        await send_button.click()

    async def wait_and_extract_response(self, target_index: int) -> str:
        target_turn = self.page.locator(self._assistant_sections).nth(target_index)
        container = target_turn.locator(self._inner_markdown)
        
        await container.wait_for(state="visible", timeout=15000)
        
        previous_length = 0
        stable_cycles = 0
        
        while stable_cycles < 4:
            await asyncio.sleep(0.5)
            current_text = await container.inner_text()
            current_length = len(current_text.strip())
            
            if current_length > 0 and current_length == previous_length:
                stable_cycles += 1
            else:
                stable_cycles = 0
                
            previous_length = current_length
            
        final_text = await container.inner_text()
        return final_text.strip()
