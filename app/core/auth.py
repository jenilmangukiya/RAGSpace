import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials  # ✅ Extracts Bearer token cleanly

    try:
        supabase_url = settings.SUPABASE_URL.split(".co")[0] + ".co"

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
            )

        if res.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return res.json()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
