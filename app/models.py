from datetime import datetime
from typing import Union, Any, List

from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, model_validator


# Base models
class CategoryBase(SQLModel):
    name: str
    parent_id: int | None = Field(default=None, foreign_key="category.id")


class ProductImageBase(SQLModel):
    zoom_url: str
    regular_url: str
    thumbnail_url: str
    perspective: int


class NutritionalInformationBase(SQLModel):
    calories: float | None
    total_fat: float | None
    saturated_fat: float | None
    polyunsaturated_fat: float | None
    monounsaturated_fat: float | None
    trans_fat: float | None
    total_carbohydrate: float | None
    dietary_fiber: float | None
    total_sugars: float | None
    protein: float | None
    salt: float | None


class ProductBase(SQLModel):
    id: str = Field(primary_key=True)
    ean: str
    slug: str
    brand: str | None
    name: str
    price: float
    category_id: int = Field(foreign_key="category.id")
    description: str | None
    origin: str | None
    packaging: str | None
    unit_name: str | None
    unit_size: float | None
    is_variable_weight: bool = False
    is_pack: bool = False


class PriceHistoryBase(SQLModel):
    price: float
    timestamp: datetime


# DB models
class Category(CategoryBase, table=True):
    id: int = Field(primary_key=True)
    products: list["Product"] = Relationship(back_populates="category")


class ProductImage(ProductImageBase, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: str = Field(foreign_key="product.id")
    product: "Product" = Relationship(back_populates="images")


class NutritionalInformation(NutritionalInformationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: str = Field(foreign_key="product.id")
    product: "Product" = Relationship(back_populates="nutritional_information")


class Product(ProductBase, table=True):
    category: Category = Relationship(back_populates="products")
    images: List[ProductImage] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "joined"}
    )
    price_history: List["PriceHistory"] = Relationship(back_populates="product")
    nutritional_information: Union[NutritionalInformation, None] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "joined"}
    )


class PriceHistory(PriceHistoryBase, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: str = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="price_history")


# Public models
class CategoryPublic(CategoryBase):
    id: int


class ProductImagePublic(ProductImageBase):
    id: int
    product_id: str


class NutritionalInformationPublic(NutritionalInformationBase):
    id: int
    product_id: str


class ProductPublic(ProductBase):
    category: CategoryPublic
    images: List[ProductImagePublic] = []
    nutritional_information: NutritionalInformationPublic | None = None
    price_history: List["PriceHistoryPublic"] = []


class PriceHistoryPublic(PriceHistoryBase):
    id: int
    product_id: str


# Other models (unchanged)
class ItemStats(BaseModel):
    calories: float | None
    proteins: float | None
    carbs: float | None
    fat: float | None
    fiber: float | None
    cost_per_daily_kcal: float | None
    cost_per_100g_protein: float | None
    cost_per_100g_carb: float | None
    cost_per_100g_fat: float | None
    kcal_per_euro: float | None


class TicketItem(BaseModel):
    product: ProductPublic
    original_name: str
    quantity: int
    unit_price: float
    total_price: float
    stats: ItemStats | None


class TicketStats(BaseModel):
    items: List[TicketItem]


class ProductMatch(BaseModel):
    score: float
    product: ProductPublic


def default_quantity(v: Any) -> int:
    if v is None:
        return 1
    return v


class TicketInfo(BaseModel):
    ticket_number: int | None = None
    date: str | None = None
    time: str | None = None
    total_price: float | None = None
    items: list[TicketItem]

    @model_validator(mode="after")
    def guess_total(self):
        if self.total_price is None:
            self.total_price = sum(
                item.total_price for item in self.items if item.total_price is not None
            )
        return self


class ProductInfo(BaseModel):
    product: ProductPublic
    is_food: bool
    total_weight: float | None = None
    total_calories: float | None = None
    total_protein: float | None = None
    total_carbs: float | None = None
    total_fat: float | None = None


class ExtractedTicketItem(BaseModel):
    name: str
    quantity: int
    total_price: float
    unit_price: float


class ExtractedTicketInfo(BaseModel):
    ticket_number: int | None
    date: str | None
    time: str | None
    total_price: float | None
    items: List[ExtractedTicketItem]
