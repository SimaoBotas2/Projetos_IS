from datetime import datetime

from sqlmodel import Session, select

from app.models import Author, AuthorCreate, AuthorUpdate, Book, BookCreate, BookUpdate


class AuthorNotFoundError(Exception):
    pass


class AuthorHasBooksError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


def _validate_book_year(year: int) -> None:
    current_year = datetime.now().year
    if year < 0:
        raise ValueError("Year must be a positive number")
    if year > current_year:
        raise ValueError("Year cannot be in the future")


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