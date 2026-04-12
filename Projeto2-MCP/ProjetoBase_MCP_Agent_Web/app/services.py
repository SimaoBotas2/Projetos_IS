from sqlmodel import Session, select

from app.models import Book, BookCreate, BookUpdate, Author, AuthorCreate, AuthorUpdate

class AuthorNotFoundError(Exception):
    pass

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

def update_author(session:Session, author_id: int, data: AuthorUpdate) -> Author:
    author = get_author(session, author_id)
    update = data.model_dump(exclude_unset=True)
    for key, value in update.items():
        setattr(author, key, value)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

def delete_author(session: Session, author_id: int) -> dict:
    author = get_author(session, author_id)
    session.delete(author)
    session.commit()
    return {"status": "deleted", "id": author_id}


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