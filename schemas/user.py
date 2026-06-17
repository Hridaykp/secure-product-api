from pydantic import BaseModel

# User registration and login schemas
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str 
    password: str
