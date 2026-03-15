from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
mongo_uri = "mongodb://localhost:27017/"

app = FastAPI()

client = MongoClient(mongo_uri)
db = client["fastapi_db"]             # here we give as DB name
products_collection = db["products"]  # witin DB name, it is collection name


# for serialization in dictionary
def product_serializer(product) -> dict:
    return{
        # "id": product["id"],
        "_id": str(product["_id"]),
        "name" : product["name"],
        "price": product["price"]
    }


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
    product = products_collection.find_one(
        {"_id":ObjectId(id)}
    )
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
    


dbs = client.list_database_names()
print(dbs)
