from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class BookBase(SQLModel):
    title: str
    author: str
    year: int
    available: bool = Field(default=True)


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BookCreate(BookBase):
    pass


class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    available: Optional[bool] = Field(default=None)
