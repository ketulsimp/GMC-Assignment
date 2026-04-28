from pydantic import BaseModel,Field,HttpUrl,field_validator,StringConstraints
from typing import Optional,List,Annotated
from decimal import Decimal
from fastapi_service.models.db_model import products
from custom_logs.custom_logger import logger

nameString=Annotated[str,StringConstraints(max_length=100)]
descString=Annotated[str,StringConstraints(max_length=500)]

class Products(BaseModel):
    product_id:int=Field(...,ge=1)
    product_name:nameString=Field(...,max_length=100)
    description:descString=Field(...,max_length=500)
    price:Decimal=Field(...,gt=0,max_digits=8,decimal_places=2)
    category:str=Field(...,max_length=100)
    sku:str=Field(...,max_length=25)
    images:Optional[List[HttpUrl]]=Field(default=None,max_length=10) 

    @field_validator("product_id")
    @classmethod
    def check_id(cls,id):
        query=products.find_one({'product_id':id})
        if query:
            logger.error(f'Product id not unique. Product with id:{id} already exist')
            raise ValueError('Value must be unique')
        return id
    
    @field_validator("price")
    @classmethod
    def check_price(cls,price):
        if price<0:
            logger.error("Price should be greater than 0")
            raise ValueError('Price must be greater than zero')
        return price
    
    @field_validator("sku")
    @classmethod
    def check_sku(cls,sku):
        if not sku.replace("-","").isalnum():
            logger.error("SKU should be unique")
            raise ValueError('Value must be alpha-numeric')
        return sku