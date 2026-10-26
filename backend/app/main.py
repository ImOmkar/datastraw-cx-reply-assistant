from fastapi import FastAPI

from backend.app.api.routes.brands import router as brands_router
from backend.app.api.routes.knowledge_base import router as knowledge_base_router
from backend.app.api.routes.conversations import router as conversations_router
from backend.app.api.routes.messages import router as messages_router
from backend.app.api.routes.reply_drafts import router as reply_drafts_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Datastraw CX Reply Assistant",
    description="AI-powered customer experience reply assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands_router)
app.include_router(knowledge_base_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(reply_drafts_router)


@app.get("/")
def root():
    return {
        "message": "Datastraw CX Reply Assistant API is running"
    }
    
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }