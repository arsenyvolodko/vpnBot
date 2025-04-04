from pydantic import BaseModel


class Message(BaseModel):
    text: str
    only_to_me: bool = True


class UserSubscriptionUpdates(BaseModel):
    user: int
    total_price: int
    renewed: list[str]
    stopped_due_to_lack_of_funds: list[str]
    stopped_due_to_offed_auto_renew: list[str]
    deleted: list[str]


class SubscriptionUpdates(BaseModel):
    is_reminder: bool
    updates: list[UserSubscriptionUpdates]
