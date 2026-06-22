from app.models import subscription
from datetime import timedelta
from datetime import datetime
from app.models.subscription import Subscription
from app.enums.subscription import (
    PricingPlan,
    SubscriptionStatus,
)


class SubscriptionService:
    def __init__(self, db):
        self.db = db

    def get_or_create_subscription(
        self,
        user_id: str,
    ):
        subscription = (
            self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
        )

        if not subscription:
            subscription = Subscription(
                user_id=user_id,
                plan_name=PricingPlan.TRIAL,
                stripe_subscription_id=None,
                stripe_price_id=None,
                status=SubscriptionStatus.ACTIVE,
                trial_ends_at=datetime.utcnow() + timedelta(days=7),
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription

        if (
            subscription.plan_name == PricingPlan.TRIAL
            and subscription.trial_ends_at
            and subscription.trial_ends_at < datetime.utcnow()
        ):
            subscription.plan_name = PricingPlan.INACTIVE
            subscription.status = SubscriptionStatus.EXPIRED

            self.db.commit()
        return subscription
