from fastapi import APIRouter, Depends
from fastapi import HTTPException
from .auth import role_required
from database.connection import users_collection


router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin-only endpoint
@router.post("/make-admin/{username}")
def make_admin(username: str, current_user: dict = Depends(role_required(["admin"]))):
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"role": "admin"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"{username} is now admin"}


# Admin dashboard endpoint
@router.get("/dashboard")
def admin_dashboard(current_user: dict = Depends(role_required(["admin"]))):
    return {
        "message": "Welcome to the admin dashboard !",
        "user": current_user
    }