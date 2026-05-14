from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class AuthorBase(SQLModel):
    name: str
    age: int
    country: str


class Author(AuthorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(SQLModel):
    name: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None


class BookBase(SQLModel):
    title: str
    year: int
    available: bool = Field(default=True)
    cost_price: float
    sale_price: float


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author: str = Field(index=True)
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")


class BookCreate(BookBase):
    author_id: int


class BookUpdate(SQLModel):
    title: Optional[str] = None
    year: Optional[int] = None
    available: Optional[bool] = Field(default=None)
    author_id: Optional[int] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None


# Analytics Models
class CountryBase(SQLModel):
    name: str
    region: str


class Country(CountryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CountryCreate(CountryBase):
    pass


class CountryUpdate(SQLModel):
    name: Optional[str] = None
    region: Optional[str] = None


# Kafka Event Models
class PurchaseEvent(SQLModel):
    book_id: int
    supplier_id: int
    cost: float
    quantity: int
    timestamp: str


class SaleEvent(SQLModel):
    book_id: int
    country_id: int
    price: float
    quantity: int
    timestamp: str


class ResultEvent(SQLModel):
    metric_name: str
    key: str
    value: float
    timestamp: str