from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float

def product_serializer(product) -> dict:
    return {
        "_id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"]
    }