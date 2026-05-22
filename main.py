import asyncio
from langchain_core.messages import HumanMessage
from models import ScrapeChatModel

async def run_terminal_demo():
    print("[1/3] Initializing LangChain custom scaper model...")
    # Headless=False opens a visible chrome instance so you can bypass logins/popups manually if needed
    model = ScrapeChatModel(headless=False)
    
    messages = [HumanMessage(content="Write a 1-sentence motivational quote about coding.")]
    
    print("[2/3] Sending payload transaction via Playwright...")
    response = await model.ainvoke(messages)
    
    print("\n" + "="*40)
    print("LANGCHAIN OUTPUT RESULT:")
    print("="*40)
    print(response.content)
    print("="*40 + "\n")
    
    print("[3/3] Shutting down browser threads cleanly...")
    await model.aclose()

if __name__ == "__main__":
    # Standard terminal run mechanism
    asyncio.run(run_terminal_demo())
