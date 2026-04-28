
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
            raise ValueError("product_image must start with http:// or https://")
        domain_part = url.split("//")[-1].split("/")[0]  
        if "." not in domain_part:
            raise ValueError("product_image must have a valid domain e.g. example.com")
        extension = domain_part.split(".")[-1]
        if len(extension) < 2:
            raise ValueError("product_image domain must have a valid extension e.g. .com .org .co")
        return v
