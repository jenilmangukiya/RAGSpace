from fastapi import FastAPI, Depends
from app.core.auth import get_current_user

app = FastAPI()


@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user": user}


@app.get("/health")
async def health():
    return {"health": "ok"}
