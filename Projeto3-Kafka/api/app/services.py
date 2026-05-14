from datetime import datetime

from sqlmodel import Session, select

from app.models import (
    Author, AuthorCreate, AuthorUpdate,
    Book, BookCreate, BookUpdate,
    Country, CountryCreate, CountryUpdate,
)


class AuthorNotFoundError(Exception):
    pass


class AuthorHasBooksError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class CountryNotFoundError(Exception):
    pass


def _validate_book_year(year: int) -> None:
    current_year = datetime.now().year
    if year < 0:
        raise ValueError("Year must be a positive number")
    if year > current_year:
        raise ValueError("Year cannot be in the future")


def _parse_author_age_text(age_text: str) -> int:
    cleaned = age_text.strip()
    if not cleaned:
        raise ValueError("Age text cannot be empty")

    try:
        age = int(cleaned)
    except ValueError as exc:
        raise ValueError("Age text must contain a valid integer") from exc

    if age < 0:
        raise ValueError("Age must be a positive number")

    return age


def list_authors(session: Session) -> list[Author]:
    return session.exec(select(Author)).all()


def get_author(session: Session, author_id: int) -> Author:
    author = session.get(Author, author_id)
    if author is None:
        raise AuthorNotFoundError(f"Author {author_id} not found")
    return author


def create_author(session: Session, data: AuthorCreate) -> Author:
    author = Author.model_validate(data)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def create_author_from_text(session: Session, name: str, age_text: str, country: str) -> dict:
    age = _parse_author_age_text(age_text)
    author = create_author(
        session,
        AuthorCreate(name=name, age=age, country=country),
    )
    result = author.model_dump()
    result["age_text"] = age_text
    return result


def update_author(session: Session, author_id: int, data: AuthorUpdate) -> Author:
    author = get_author(session, author_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(author, key, value)

    linked_books = session.exec(select(Book).where(Book.author_id == author_id)).all()
    for book in linked_books:
        book.author = author.name
        session.add(book)

    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def delete_author(session: Session, author_id: int) -> dict:
    author = get_author(session, author_id)
    linked_books = session.exec(select(Book).where(Book.author_id == author_id)).all()
    if linked_books:
        raise AuthorHasBooksError(
            f"Cannot delete author {author_id} because there are books linked to this author"
        )

    session.delete(author)
    session.commit()
    return {"status": "deleted", "id": author_id}


def list_books(session: Session) -> list[Book]:
    return session.exec(select(Book)).all()


def get_book(session: Session, book_id: int) -> Book:
    book = session.get(Book, book_id)
    if book is None:
        raise BookNotFoundError(f"Book {book_id} not found")
    return book


def create_book(session: Session, data: BookCreate) -> Book:
    _validate_book_year(data.year)
    author = get_author(session, data.author_id)
    book = Book(
        title=data.title,
        year=data.year,
        available=data.available,
        author_id=author.id,
        author=author.name,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def update_book(session: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(session, book_id)
    updates = data.model_dump(exclude_unset=True)

    if "year" in updates and updates["year"] is not None:
        _validate_book_year(updates["year"])

    if "author_id" in updates and updates["author_id"] is not None:
        author = get_author(session, updates["author_id"])
        book.author_id = author.id
        book.author = author.name

    for key, value in updates.items():
        if key != "author_id":
            setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def delete_book(session: Session, book_id: int) -> dict:
    book = get_book(session, book_id)
    session.delete(book)
    session.commit()
    return {"status": "deleted", "id": book_id}


# Country CRUD operations
def list_countries(session: Session) -> list[Country]:
    return session.exec(select(Country)).all()


def get_country(session: Session, country_id: int) -> Country:
    country = session.get(Country, country_id)
    if country is None:
        raise CountryNotFoundError(f"Country {country_id} not found")
    return country


def create_country(session: Session, data: CountryCreate) -> Country:
    country = Country.model_validate(data)
    session.add(country)
    session.commit()
    session.refresh(country)
    return country


def update_country(session: Session, country_id: int, data: CountryUpdate) -> Country:
    country = get_country(session, country_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(country, key, value)
    session.add(country)
    session.commit()
    session.refresh(country)
    return country


def delete_country(session: Session, country_id: int) -> dict:
    country = get_country(session, country_id)
    session.delete(country)
    session.commit()
    return {"status": "deleted", "id": country_id}