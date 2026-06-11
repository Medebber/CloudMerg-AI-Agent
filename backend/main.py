# uvicorn main:app --reload    

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.engine import get_chat_response_stream
from dotenv import load_dotenv
import os
from fastapi.responses import StreamingResponse
import json

load_dotenv()

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    history: list[tuple[str, str]] = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set")

    def generate():
        # stream tokens from your model
        for chunk in get_chat_response_stream(
            request.message,
            request.history,
            api_key
        ):
            # Check if chunk has content and yield it as a raw string
            if chunk:
                yield str(chunk)

    # Use text/event-stream or text/plain so the frontend can read it easily
    return StreamingResponse(generate(), media_type="text/event-stream")

app.mount("/", StaticFiles(directory="frontend_build", html=True), name="frontend")
