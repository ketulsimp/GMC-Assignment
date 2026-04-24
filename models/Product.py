from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Product(BaseModel):
    id: int = Field(ge=1,le=1000)
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    image: str = Field(examples=['http://image.com'], max_length=100) 
    url: str = Field(examples=['http://url.com'], max_length=100)
    sku: str = Field(..., min_length=10, max_length=10)
    colour: str = Field(..., min_length=30)
    size: str = Field(..., max_length=5)
    createdAt: datetime = Field(default=datetime.now())
    


    @field_validator('url','image')
    def url_validator(cls, value: str):
        if not (value.startswith('http://') or value.startswith('https://')):
            raise ValueError('URL Must be start with http or https')
        else:
            return value