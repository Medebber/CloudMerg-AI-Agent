#

# uvicorn main:app --reload    

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.engine import get_chat_response_stream
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()
app = FastAPI()

# ==========================================
# 1. APPLICATION (API endpoints)
# ==========================================
base_dir = os.path.abspath(os.path.dirname(__file__))

# ==========================================
# 2. API ENDPOINTS
# ==========================================
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


# ==========================================
# 3. FRONTEND MOUNTING (Serve built React app)
#    Mount after API endpoints so routes like /chat remain reachable
# ==========================================
frontend_dirs = [
    os.path.join(base_dir, "frontend_build"),
    os.path.join(base_dir, "..", "frontend_build"),
    os.path.join(base_dir, "..", "frontend", "build"),
]

frontend_dir = next((os.path.abspath(d) for d in frontend_dirs if os.path.isdir(os.path.abspath(d))), None)

if frontend_dir:
    print(f"Serving frontend from: {frontend_dir}")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    print("WARNING: No frontend build directory found. Running backend API only.")
    @app.get("/")
    async def root_health_check():
        return {"status": "healthy", "message": "Backend is running, but frontend assets are missing."}

# ==========================================
# 4. PRODUCTION PORT BINDING FOR RENDER
# ==========================================
if __name__ == "__main__":
    # Render passes a dynamic port in os.environ. Local runs default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)