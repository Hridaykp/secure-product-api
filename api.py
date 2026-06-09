from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

mongo_uri = "mongodb://localhost:27017"

app = FastAPI()

client = MongoClient(mongo_uri)
db = client["fastapi_db"]             # here we give as DB name
products_collection = db["products"]  # within DB name, it is collection name
users_collection = db["users"]       # for user collection


SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# refresh_token_expires_minutes = 60 * 24 * 7 # 7 days

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# for serialization in dictionary
def product_serializer(product) -> dict:
    return{
        # "id": product["id"],
        "_id": str(product["_id"]),
        "name" : product["name"],
        "price": product["price"]
    }

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str 
    password: str


def hash_password(password: str):
    # print(password, len(password))
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# for creating access token with expiration time
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = 15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt 


# To get the current user based on the token provided in the request header
def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Recieved token", token)
    credentials_exception = HTTPException(
        status_code = 401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"username": username})

    if not user:
        raise credentials_exception
    
    return{
            "id": str(user["_id"]),
            "username": user["username"]
        }



# Register endpoint
@app.post("/register")
def register(user: UserRegister):
    existing_user = users_collection.find_one(
        {"username": user.username}
    )   

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    }) 

    return {"message": "User registered successfully !!"} 


# Login endpoint
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = users_collection.find_one(
        {"username": form_data.username}
    )

    if not db_user:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid username or password !!"
        )

    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(
            status_code = 400,
            detail = "Invalid username or password !!"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta = access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Protected endpoint to get user profile, accessible only with valid token
@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

#Home URL
@app.get("/")
def home_Page():
    return {
        "Home":"This is home page"
    }
  
#About page URL  
@app.get("/about")
def about_page():
    return {
        "About":"this is about page "
    }


#Fetching one product by its ID
@app.get("/products/id/{id}")
def get_productbyID(id: str):
    try:
        product = products_collection.find_one(
            {"_id":ObjectId(id)}
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    if product:
        return{
            "product":product_serializer(product),
            "message":"product fetched succesfuly"
        }
    else:
        return{"message":"prod id not found"}



#Fetching all products
@app.get("/products")
def get_Products():
    products = list(products_collection.find())
    return {
        "message":"products are here",
        "products":[product_serializer(p) for p in products]   
    }



#Fetching products (filtered with given price )
@app.get("/products/price/{price}")
def get_Product(price: int):
    response = requests.get(f"https://fakestoreapi.com/products/")
    products = response.json() 
    filetred_price = []
    for prod in products:
        lower_price = price 
        upper_price = price + 1
        if  lower_price <= prod["price"] < upper_price:
            filetred_price.append(prod)
    return filetred_price


#Data validation: Ensures that incoming data matches the types you declare.
class Product(BaseModel):
    # id: int
    name: str
    price: float



#Add product 
@app.post("/products")
def add_Product(product: Product):
    result = products_collection.insert_one(product.model_dump())
    # products.append(product.model_dump())
    return {
        "message":"product created succesfully",
        "id": str(result.inserted_id),
        "product": product
    }


#Update product
@app.put("/products/{prod_id}") 
def update_Products(prod_id: str , updated_product:Product):
    result = products_collection.update_one(
        {"_id": ObjectId(prod_id)},
        {"$set": updated_product.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="product id not found")
    return {"message":"product updated succesfuly !!"}
            

#Delete product 
@app.delete("/products/{prod_id}")
def delete_Product(prod_id: str):
    resid = products_collection.delete_one({"_id": ObjectId(prod_id)})
    if resid.deleted_count == 1:
        return {"message": "Product deleted succesfully "}
    else:
        return{"message":f"prod_id {prod_id}not found"}
    

