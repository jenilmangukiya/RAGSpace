from app.routes import documents, apps, search, chat

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth import get_current_user

app = FastAPI(
    title="RAG-space API for LLM",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user": user}


@app.get("/health")
async def health():
    return {"health": "ok"}


app.include_router(apps.router, prefix="/api/apps", tags=["Apps"])
app.include_router(
    documents.router,
    prefix="/api/apps/{app_id}/documents",
    tags=["Documents"],
)
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
