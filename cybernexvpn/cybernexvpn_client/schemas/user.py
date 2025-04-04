from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str | None
    balance: int


class CreateUserRequest(BaseModel):
    username: str | None


class ApplyInvitationRequest(BaseModel):
    inviter: int
