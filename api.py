from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
mongo_uri = "mongodb://localhost:27017/"

app = FastAPI()

client = MongoClient(mongo_uri)
db = client["fastapi_db"]   # here we give as DB name
products_collection = db["products"]  # witin DB name, it is collection name

# for serialization in dictionary
def product_serializer(product) -> dict:
    return{
        "id": str(product["_id"]),
        "name" : product["name"],
        "price": product["price"]
    }


@app.get("/")
def home_Page():
    return {
        "Home":"This is home page"
    }
  
    
@app.get("/about")
def about_page():
    return {
        "About":"this is about page"
    }


@app.get("/products")
def get_Products():
    products = list(products_collection.find())
    return {
        "message":"products are here",
        "products":[product_serializer(p) for p in products]
        
            
    }
    # response = requests.get("https://fakestoreapi.com/products")
    # return response.json()


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


class Product(BaseModel):
    # id: int
    name: str
    price: float

# products = []
    
@app.post("/products")
def add_Product(product: Product):
    result = products_collection.insert_one(product.model_dump())
    # products.append(product.model_dump())
    return {
        "message":"product created succesfully",
        "id": str(result.inserted_id),
        "product": product
    }



@app.put("/products/{prod_id}") 
def update_Products(prod_id: str , updated_product:Product):
    result = products_collection.update_one(
        {"_id": ObjectId(prod_id)},
        {"$set": updated_product.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="product id not found")
    return {"message":"product updated succesfuly !!"}
            

@app.delete("/products/{prod_id}")

def delete_Product(prod_id: int):
    for i, p in enumerate(products):
        if p["id"] == prod_id:
            del products[i]
            return {
                "message":"product deleted successfully"
            }
    return {"error":"product not found"}


