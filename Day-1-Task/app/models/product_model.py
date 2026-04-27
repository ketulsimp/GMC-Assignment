from pydantic import BaseModel, Field

class Product(BaseModel):
    title: str = Field(max_length=100,default='Product_Title')
    description: str = Field(max_length=5000,default='Product_Description')
    sku: str = Field(max_length=20,default='HK123')
    images: list = Field(max_length=10,default=["https://abc.com","https://ww.com"])
    category: str = Field(max_length=30,default="Category")
    gsin: str  = Field(max_length=20,default="132789302735634810384031")
    price: float = Field(lt=10000,default=1000)
    quantity: int = Field(lt=1000,default=100)
    