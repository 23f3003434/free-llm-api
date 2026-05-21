import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Notice: No Playwright imports here anymore
from app_modules.chat_service import (
    initialize_browser_service, 
    close_browser_service, 
    execute_chat_transaction
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Delegate initialization entirely to the chat service
    await initialize_browser_service()
    yield
    # Delegate cleanup entirely to the chat service
    await close_browser_service()

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def process_chat_endpoint(payload: ChatRequest):
    try:
        # Service manages its own shared page reference internally
        ai_response_text = await execute_chat_transaction(payload.message)
        return ChatResponse(response=ai_response_text)
    except RuntimeError as service_error:
        raise HTTPException(status_code=503, detail=str(service_error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
