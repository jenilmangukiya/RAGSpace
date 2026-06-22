from enum import Enum


class PricingPlan(str, Enum):
    TRIAL = "trial"
    PRO = "pro"
    PREMIUM = "premium"
    INACTIVE = "inactive"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"
