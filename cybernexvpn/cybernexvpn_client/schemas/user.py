from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str | None
    first_name: str | None = None
    balance: int
    token: str


class CreateUserRequest(BaseModel):
    username: str | None
    first_name: str | None = None


class PatchUserRequest(BaseModel):
    username: str | None = None
    first_name: str | None = None


class ApplyInvitationRequest(BaseModel):
    inviter: int
