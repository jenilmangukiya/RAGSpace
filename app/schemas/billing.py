# schemas/billing.py

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    price_id: str
