from fastapi import FastAPI
from routers import auth, products

app = FastAPI(title="E-Comm(FastAPI)")

# Include routers for authentication and product management
app.include_router(auth.router)
app.include_router(products.router)

# General endpoints 
@app.get("/", tags=["General"])
def home_Page():
    return {"Home": "This is home page"}


@app.get("/about", tags=["General"])
def about_page():
    return {"About": "this is about page "}
