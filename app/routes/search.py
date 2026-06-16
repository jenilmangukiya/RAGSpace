from fastapi import (
    APIRouter,
    Depends,
)

from app.core.auth import (
    get_current_user,
)
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
)
from app.services.search_service import (
    SearchService,
)

router = APIRouter()


@router.post(
    "/",
    response_model=SearchResponse,
)
def search_endpoint(
    payload: SearchRequest,
    current_user=Depends(get_current_user),
):
    results = SearchService.search(
        query=payload.query,
        user_id=current_user["id"],
        app_id=str(payload.app_id),
    )

    return {"results": results}
