from app.services.billing_service import BillingService
from app.db.dependencies import get_db
from fastapi import Depends
from app.core.config import settings
from fastapi import APIRouter, Request, HTTPException
import stripe

router = APIRouter()


@router.post("/stripe")
async def webhook(request: Request, db=Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook",
        )

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        service = BillingService(db)
        service.handle_checkout_completed(event)
    elif event_type == "customer.subscription.updated":
        service = BillingService(db)
        service.handle_subscription_updated(event)
    elif event_type == "customer.subscription.deleted":
        service = BillingService(db)
        service.handle_subscription_deleted(event)

    return {"received": True}
