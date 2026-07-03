from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from database.connection import users_collection
from schemas.user import UserRegister
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import hash_password, verify_password, create_access_token
# from fastapi.responses import JSONResponse


router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"username": username})

    if not user:
        raise credentials_exception
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user")  # Default role is "user" if not specified
    }


# Dependency to check if the current user has the required role
def role_required(allowed_roles: list):
    def wrapper(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return wrapper



@router.get("/admin-only")
def admin_only_endpoint(current_user: dict = Depends(role_required(["admin"]))):
   return {
       "message": "Welcome, admin! You have access to this endpoint.",
       "user": current_user
   }


# User registration endpoint
@router.post("/register")
def register(user: UserRegister):
    existing_user = users_collection.find_one({"username": user.username})   
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password),
        "role": "user"          # Default role is "user" 
    }) 
    
    return {"message": "User registered successfully !!"} 



# User login endpoint
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = users_collection.find_one({"username": form_data.username})

    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password !!")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username,
        "role": db_user.get("role", "user")},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

    



# Endpoint to get user profile
@router.get("/profile")
def get_profile(current_user: dict = Depends(role_required(["user", "admin"]))):   # Both "user" and "admin" can access this endpoint
    return current_user 