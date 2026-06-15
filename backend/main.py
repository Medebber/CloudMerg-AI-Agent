# uvicorn main:app --reload    

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.engine import get_chat_response_stream
from dotenv import load_dotenv
import os

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

base_dir = os.path.abspath(os.path.dirname(__file__))
frontend_dirs = [
    os.path.join(base_dir, "frontend_build"),
    os.path.join(base_dir, "..", "frontend_build"),
    os.path.join(base_dir, "..", "frontend", "build"),
]
frontend_dir = next((os.path.abspath(d) for d in frontend_dirs if os.path.isdir(os.path.abspath(d))), None)
if frontend_dir:
    print(f"Serving frontend from: {frontend_dir}")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
