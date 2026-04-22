from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from utils import llm
import logging

app = FastAPI(title="My API", description="This is a sample API", version="1.0.0")

LOG = logging.getLogger(__name__)
LOG.info("API is starting up")
LOG.info(uvicorn.Config.asgi_version)


class MessageEntry(BaseModel):
    role: str
    content: str


class QueryData(BaseModel):
    user_prompt: str
    screenshot_b64: str
    screen_width: int
    screen_height: int
    history: Optional[List[MessageEntry]] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload-text")
def receive_query(data: QueryData):
    print(f"User said: {data.user_prompt}")
    print(f"Screenshot size: {data.screen_width}x{data.screen_height}")

    history = None
    if data.history:
        history = [{"role": m.role, "content": m.content} for m in data.history]

    result = llm.sendMessage(
        data.user_prompt,
        data.screenshot_b64,
        data.screen_width,
        data.screen_height,
        history,
    )

    LOG.info(f"LLM response: {result['response']}")
    return result
