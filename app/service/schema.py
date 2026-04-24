from pydantic import BaseModel,Field,field_validator
from typing import List,Annotated

class Product(BaseModel):
    product_id : Annotated[int,Field(le=9999999999,ge=1,title='product_id',description='must be unique for all product',example=2)]
    name : Annotated[str,Field(max_length=20,title='product_name',description='product name',example='pant')]
    sku : Annotated[str,Field(max_length=15,min_length=8,title='product_sku',description='must be unique for all product',example='CL-SAN-LT-8-BLU')]
    photo : Annotated[List[str],Field(max_length=1000,title='produt_photo_url',description='url of the product photo and url must start from https',example=['https.exaple.con'])]
    description : Annotated[str,Field(max_length=1000,title='product_description',description='full detail about the product',example='this is the product of ...')]
    gtin : Annotated[float,Field(le=99999999999999,ge=11111111,title='product_gtin',description='global trade iteam number of the product',example=4012345123456)] 
    price : Annotated[float,Field(le=100000000000,ge=1,title='product_price',description='price at which the product is to sell',example=2000)]
    product_type : Annotated[str,Field(max_length=50,title='product_family',description='type of the product',example='electronics')]
    
    @field_validator('photo')
    @classmethod
    def url_validation(cls,value):
        if len(value) > 10:
            raise ValueError('less then 10 photo allowed')
        for i in value:
            if i[0:5] != 'https':
                raise ValueError('only secure https link allowed')
        return value