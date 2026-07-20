from pydantic import BaseModel

# User registration and login schemas
class UserRegister(BaseModel):
    username: str
    password: str
    role: str       # Role can be "admin" or "user"

class UserLogin(BaseModel):
    username: str 
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Tokens(BaseModel):
    username: str
    token: str
    token_type: str
    revoked: bool = False
    created_at: str | None = None
    expires_at: str | None = None