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
    author: str
    year: int
    available: bool = Field(default=True)


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int | None = Field(default=None, foreign_key="author.id")


class BookCreate(BookBase):
    pass


class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    available: Optional[bool] = Field(default=None)