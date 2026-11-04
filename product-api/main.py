""" Cisco M2S2 Demo 01: beginer Product CRUD API (in-memory storage)"""
import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from starlette.exceptions import HTTPException as StarletteHTTPException

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


from pydantic import BaseModel, Field 


app = FastAPI(
    title="Product API",
    version="1.0.0",
    description="Beginner CRUD API used in the Cisco AI Apprenticeship FastAPI lab.",
)

# Pydantic Models

class ProductBase(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    in_stock: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    in_stock: Optional[bool] = None


class Product(ProductBase):
    id: int


products: dict[int, Product] = {
    1: Product(id=1, name="Router", price=30000.0, in_stock=True),
    2: Product(id=2, name="Switch", price=23000.0, in_stock=True),
}
next_id = 3



ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30


DEMO_USERNAME = os.getenv("DEMO_USERNAME")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")


if not DEMO_USERNAME or not DEMO_PASSWORD or not JWT_SECRET:
    raise RuntimeError(
        "Set DEMO_USERNAME, DEMO_PASSWORD and JWT_SECRET environment variables before starting the app."
    )

password_hash = PasswordHash.recommended()
demo_user = {
    "username": DEMO_USERNAME,
    "password_hash": password_hash.hash(DEMO_PASSWORD),
}

#URL from where the client would get the access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def authenticate(username: str, password: str) -> bool:
    return (
        username == demo_user["username"]
        and password_hash.verify(password, demo_user["password_hash"])
    )

def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": subject, "exp": expires}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    code = "DEVICE_NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail), "status": exc.status_code}}
    )


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != demo_user["username"]:
            raise credentials_error
        return str(username)
    except InvalidTokenError:
        raise credentials_error



@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    if not authenticate(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(form.username),
        "token_type": "bearer",
    }


# Implement the Home Page

@app.get("/")
def home():
    return {"message":"server Started"}

# Implement the /products endpoint

@app.get("/products")
def  list_products(current_user: str = Depends(get_current_user)):
    return list(products.values())

# Implement the /products/{product_id}


@app.get("/products/{product_id}", response_model = Product)
def  get_product(product_id: int,current_user: str = Depends(get_current_user)):
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Implement new Product creation 
@app.post("/products", status_code=status.HTTP_201_CREATED,response_model=Product)
def create_product(request_payload: ProductCreate, current_user: str = Depends(get_current_user)):
    global next_id
    product = Product(id=next_id, **request_payload.model_dump())
    products[next_id] = product
    next_id += 1 
    return product

# Implement replace an existing product 

@app.put("/products/{product_id}", response_model=Product)
def replace_product(product_id: int, payload: ProductCreate,current_user: str = Depends(get_current_user)):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    product = Product(id=product_id, **payload.model_dump())
    products[product_id] = product
    return product

# Implement updating existing product

@app.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductUpdate,current_user: str = Depends(get_current_user)):
    if product_id not in products:
            raise HTTPException(status_code=404, detail="Product not found")
    existing_product = products.get(product_id)
    updates = payload.model_dump(exclude_unset=True)
    product = existing_product.model_copy(update=updates)

    #Validate the assembled product, including any explicitly supplied nulls

    product = Product.model_validate(product.model_dump())
    products[product_id] = product
    return product

# Deleteing a product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delet_product(product_id: int,current_user: str = Depends(get_current_user)):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    del products[product_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

