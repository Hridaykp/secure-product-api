import requests
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId

from database.connection import products_collection
from schemas.product import Product, product_serializer


router = APIRouter(prefix="/products", tags=["Products"])

@router.get("")
def get_Products():
    products = list(products_collection.find())
    return {
        "message": "products are here",
        "products": [product_serializer(p) for p in products]   
    }   

# Get product by ID
@router.get("/id/{id}")
def get_productbyID(id: str):
    try:
        product = products_collection.find_one({"_id": ObjectId(id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    if product:
        return {
            "product": product_serializer(product),
            "message": "product fetched successfully"
        }
    raise HTTPException(status_code=404, detail="Product ID not found")


# Get products by price range
@router.get("/price/{price}")
def get_Product(price: int):
    response = requests.get("https://fakestoreapi.com/products/")
    products = response.json() 
    filtered_price = []
    for prod in products:
        if price <= prod["price"] < (price + 1):
            filtered_price.append(prod)
    return filtered_price


# Get products 
@router.post("")
def add_Product(product: Product):
    result = products_collection.insert_one(product.model_dump())
    return {
        "message": "product created successfully",
        "id": str(result.inserted_id),
        "product": product
    }


# Update product by ID
@router.put("/{prod_id}") 
def update_Products(prod_id: str, updated_product: Product):
    try:
        result = products_collection.update_one(
            {"_id": ObjectId(prod_id)},
            {"$set": updated_product.model_dump()}
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="product id not found")
    return {"message": "product updated successfully !!"}
            

# Delete product by ID
@router.delete("/{prod_id}")
def delete_Product(prod_id: str):
    try:
        resid = products_collection.delete_one({"_id": ObjectId(prod_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    if resid.deleted_count == 1:
        return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail=f"prod_id {prod_id} not found")