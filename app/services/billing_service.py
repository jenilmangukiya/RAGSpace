from app.models import subscription
from datetime import datetime
from fastapi import HTTPException
from app.services import chunk_service
from app.models.subscription import Subscription
from app.integrations.stripe import stripe
from app.core.config import settings
from app.enums.subscription import (
    PricingPlan,
    SubscriptionStatus,
)


"""
| Plan     | Status   | Meaning                       |
| -------- | -------- | ----------------------------- |
| trial    | active   | User is in 7-day trial        |
| pro      | active   | Paying Pro customer           |
| premium  | active   | Paying Premium customer       |
| pro      | past_due | Payment failed, retrying      |
| inactive | expired  | Trial ended, never subscribed |
| inactive | canceled | Had subscription but canceled |
"""

PRICE_TO_PLAN = {
    settings.STRIPE_PRO_MONTHLY_PRICE_ID: PricingPlan.PRO,
    settings.STRIPE_PRO_YEARLY_PRICE_ID: PricingPlan.PRO,
    settings.STRIPE_PREMIUM_MONTHLY_PRICE_ID: PricingPlan.PREMIUM,
    settings.STRIPE_PREMIUM_YEARLY_PRICE_ID: PricingPlan.PREMIUM,
}


class BillingService:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def validate_access(
        subscription: Subscription,
    ):
        if (
            subscription.plan_name == PricingPlan.TRIAL
            and subscription.trial_ends_at
            and subscription.trial_ends_at < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=403, detail="Trial expired. Please upgrade."
            )

    def create_checkout_session(self, user_id, price_id):
        subscription = (
            self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
        )

        if subscription is None:
            raise HTTPException(status_code=404, detail="Subscription not found.")

        customer_id = subscription.stripe_customer_id

        if not customer_id:
            customer = stripe.Customer.create(
                metadata={
                    "user_id": user_id,
                }
            )
            customer_id = customer.id

            subscription.stripe_customer_id = customer_id
            try:
                self.db.commit()
                self.db.refresh(subscription)
            except Exception as e:
                self.db.rollback()
                raise e

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url="http://localhost:3000/payment/success",
            cancel_url="http://localhost:3000/payment/cancel",
        )

        return session.url

    def handle_checkout_completed(self, event):
        session = event["data"]["object"]

        customer_id = session["customer"]
        subscription_id = session["subscription"]

        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        print("stripe_subscription", stripe_subscription)
        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_customer_id == customer_id)
            .first()
        )

        if not subscription:
            return

        subscription.stripe_subscription_id = subscription_id

        item = stripe_subscription["items"]["data"][0]
        subscription.stripe_price_id = item["price"]["id"]

        subscription.status = stripe_subscription["status"]

        subscription.current_period_start = datetime.utcfromtimestamp(
            item["current_period_start"]
        )

        subscription.current_period_end = datetime.utcfromtimestamp(
            item["current_period_end"]
        )

        subscription.plan_name = PRICE_TO_PLAN.get(
            subscription.stripe_price_id,
            PricingPlan.TRIAL,
        )

        self.db.commit()

    def handle_subscription_updated(self, event):
        stripe_subscription = event["data"]["object"]

        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_subscription["id"])
            .first()
        )

        if not subscription:
            return

        item = stripe_subscription["items"]["data"][0]

        price_id = item["price"]["id"]

        subscription.plan_name = PRICE_TO_PLAN.get(
            price_id,
            PricingPlan.TRIAL,
        )

        subscription.status = stripe_subscription["status"]

        subscription.stripe_price_id = price_id

        subscription.cancel_at_period_end = stripe_subscription["cancel_at_period_end"]

        subscription.current_period_start = datetime.utcfromtimestamp(
            item["current_period_start"]
        )

        subscription.current_period_end = datetime.utcfromtimestamp(
            item["current_period_end"]
        )

        self.db.commit()

    def handle_subscription_deleted(self, event):
        stripe_subscription = event["data"]["object"]

        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_subscription["id"])
            .first()
        )

        if not subscription:
            return

        subscription.plan_name = PricingPlan.INACTIVE
        subscription.status = SubscriptionStatus.CANCELED

        subscription.stripe_subscription_id = None
        subscription.stripe_price_id = None
        subscription.current_period_start = None

        subscription.current_period_end = None

        subscription.cancel_at_period_end = False

        self.db.commit()
