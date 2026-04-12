from sqlmodel import Session, select

from app.models import Book, BookCreate, BookUpdate


class BookNotFoundError(Exception):
    pass


def list_books(session: Session) -> list[Book]:
    return session.exec(select(Book)).all()


def get_book(session: Session, book_id: int) -> Book:
    book = session.get(Book, book_id)
    if book is None:
        raise BookNotFoundError(f"Book {book_id} not found")
    return book


def create_book(session: Session, data: BookCreate) -> Book:
    book = Book.model_validate(data)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def update_book(session: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(session, book_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
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