import time
from playwright.sync_api import Page

class ChatGPTPage:
    def __init__(self, page: Page):
        self.page = page
        self._input_xpath = "xpath=/html/body/div/div/div/div/div/div/main/div/div/div/div/div/div/div/div/div/div/form/div/div/div/div/div/p"
        self._send_button_testid = "send-button"
        self._assistant_sections = 'section[data-turn="assistant"]'
        self._inner_markdown = 'div[data-message-author-role="assistant"] div.markdown'

    def prepare_and_type_prompt(self, prompt_text: str):
        text_field = self.page.locator(self._input_xpath)
        text_field.wait_for(state="visible", timeout=200)
        text_field.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        text_field.fill(prompt_text)

    def get_assistant_turn_count(self) -> int:
        return self.page.locator(self._assistant_sections).count()

    def click_send(self):
        send_button = self.page.get_by_test_id(self._send_button_testid)
        send_button.wait_for(state="visible", timeout=100)
        send_button.click()

    def wait_and_extract_response(self, target_index: int) -> str:
        target_turn = self.page.locator(self._assistant_sections).nth(target_index)
        container = target_turn.locator(self._inner_markdown)
        container.wait_for(state="visible", timeout=15000)
        
        previous_length = 0
        stable_cycles = 0
        
        while stable_cycles < 4:
            time.sleep(0.5)
            current_text = container.inner_text()
            current_length = len(current_text.strip())
            
            if current_length > 0 and current_length == previous_length:
                stable_cycles += 1
            else:
                stable_cycles = 0
            previous_length = current_length
            
        return container.inner_text().strip()
