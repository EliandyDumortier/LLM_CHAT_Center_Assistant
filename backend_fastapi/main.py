from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Call Center Chat Center",
    description="FastAPI backend for Chat Center",
    version="0.1.0"
)

origins = [
    "http://localhost:8000",  # Django site
    "http://localhost:3000"   # React widget/console
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response_id: str
    suggestions: list[str]

@app.post("/chat/send", response_model=ChatResponse)
async def send_chat(request: ChatRequest):
    # TODO: save request, run RAG, generate real suggestions
    stub = [
        "Thank you for reaching out. How can I assist you today?",
        "Please provide more details so I can help you better."
    ]
    return ChatResponse(response_id="resp_1", suggestions=stub)
