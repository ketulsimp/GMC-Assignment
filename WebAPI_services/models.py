
from pydantic import BaseModel, Field, HttpUrl, field_validator


class Product(BaseModel):
    product_id: int = Field(..., le=600)
    product_name: str = Field(..., max_length=30)
    sku: str = Field(..., max_length=60)
    product_image: HttpUrl
    price: float = Field(..., le=60000000)
    description: str = Field(..., max_length=2000)

    @field_validator("product_image", mode="before")
    @classmethod
    def validate_image_url(cls, v):
        url = str(v)
        if not url.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        if "." not in url.split("//")[-1]:
            raise ValueError("url must be a valid URL with a domain")
        return v