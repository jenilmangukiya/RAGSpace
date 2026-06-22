from app.services.subscription import SubscriptionService
from app.services.billing_service import BillingService
from app.schemas.billing import CheckoutRequest
from app.core.auth import get_current_user
from app.db.dependencies import get_db
from fastapi import APIRouter, Depends


router = APIRouter()


@router.get("/subscription")
def get_subscription(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = service.get_or_create_subscription(str(current_user["id"]))
    return {
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "trial_ends_at": subscription.trial_ends_at,
    }


@router.post("/checkout")
def create_checkout_session(
    payload: CheckoutRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    service = BillingService(db)
    return service.create_checkout_session(str(current_user["id"]), payload.price_id)
