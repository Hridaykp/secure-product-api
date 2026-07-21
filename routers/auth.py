from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from database.connection import users_collection, tokens_collection
from schemas.user import UserRegister, RefreshTokenRequest, LogoutRequest
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from core.security import hash_password, verify_password, create_access_token, create_refresh_token
# from fastapi.responses import JSONResponse


router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Function to store tokens in the database
def store_token(username: str, token: str, token_type: str, expires_delta: timedelta):
    now = datetime.now(timezone.utc)
    tokens_collection.insert_one({
        "username": username,
        "token": token,
        "token_type": token_type,
        "revoked": False,
        "created_at": now,
        "expires_at": now + expires_delta,
    })
    

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

        if not username or payload.get("type") != "access":
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    stored_token = tokens_collection.find_one({
        "username": username,
        "token": token,
        "token_type": "access",
        "revoked": False,
    })   

    if not stored_token:
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
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": form_data.username,
        "role": db_user.get("role", "user")},
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        data={"sub": form_data.username },
        expires_delta=refresh_token_expires
    )
    # store the tokens in the database
    store_token(form_data.username, access_token, "access", access_token_expires)
    store_token(form_data.username, refresh_token, "refresh", refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    } 



# Refresh token endpoint
@router.post("/refresh-token")
def refresh_token(request: RefreshTokenRequest):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid refresh token"
    )

    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")

        if not username or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    stored_refresh_token = tokens_collection.find_one({
        "username": username,
        "token": request.refresh_token,
        "token_type": "refresh",
        "revoked": False,
    })

    if not stored_refresh_token:
        raise credentials_exception

    db_user = users_collection.find_one({"username": username})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    new_access_token = create_access_token(
        data={"sub": username,
              "role": db_user.get("role", "user")
        },
        expires_delta=access_token_expires
    )

    tokens_collection.update_many(
        {"username": username, "token_type": "access", "revoked": False},
        {"$set": {"revoked": True}}
    )
    store_token(username, new_access_token, "access", access_token_expires)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# Logout endpoint
@router.post("/logout")
def logout(request: LogoutRequest, current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    print("Logout request received for user:", current_user["username"])
    tokens_collection.update_one({
            "username": current_user["username"],
            "token": token,
            "token_type": "access",
            "revoked": False,
        },
        {
            "$set" : {"revoked": True}
        } 
    ) 

    tokens_collection.update_one({
            "username": current_user["username"],
            "token": request.refresh_token,
            "token_type": "refresh",
            "revoked": False,
        },
        {
            "$set" : {"revoked": True}
        } 
    )

    return {"message": "Logged out successfully !!"}
 
# Endpoint to get user profile
@router.get("/profile")
def get_profile(current_user: dict = Depends(role_required(["user", "admin"]))):   # Both "user" and "admin" can access this endpoint
    return current_user 



