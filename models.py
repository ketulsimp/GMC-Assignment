from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class Product(BaseModel):
    product_id: int = Field(..., le=600)
    product_name: str = Field(..., max_length=30)
    sku: str = Field(..., max_length=60)
    product_image: HttpUrl
    price: float = Field(..., le=60000000)
    description: str = Field(..., max_length=2000)
    


