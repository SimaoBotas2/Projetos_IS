from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from app.db import create_db_and_tables, get_session
from app.models import BookCreate, BookUpdate, AuthorCreate, AuthorUpdate
from app.services import (
    BookNotFoundError,
    create_book,
    delete_book,
    get_book,
    list_books,
    update_book,
    AuthorNotFoundError,
    create_author,
    delete_author,
    get_author,
    list_authors,
    update_author,
)

app = FastAPI(title="Library REST API")

#
@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/")
def read_root():
    return {
        "message": "Library REST API is running",
        "endpoints": [
                        "GET /books", "GET /books/{id}", "POST /books", "PATCH /books/{id}", "DELETE /books/{id}", 
                        "GET /authors", "GET /authors/{id}", "POST /authors", "PATCH /authors/{id}", "DELETE /authors/{id}",
                     ],
    }

#Book CRUD methods

@app.get("/books")
def read_books(session: Session = Depends(get_session)):
    return list_books(session)


@app.get("/books/{book_id}")
def read_book(book_id: int, session: Session = Depends(get_session)):
    try:
        return get_book(session, book_id)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/books")
def create_book_endpoint(data: BookCreate, session: Session = Depends(get_session)):
    return create_book(session, data)


@app.patch("/books/{book_id}")
def update_book_endpoint(
    book_id: int, data: BookUpdate, session: Session = Depends(get_session)
):
    try:
        return update_book(session, book_id, data)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/books/{book_id}")
def delete_book_endpoint(book_id: int, session: Session = Depends(get_session)):
    try:
        return delete_book(session, book_id)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

#Author CRUD methods

@app.get("/authors")
def read_authors(session: Session = Depends(get_session)):
    return list_authors(session)

@app.get("/authors/{author_id}")
def read_author(author_id: int, session: Session = Depends(get_session)):
    try:
        return get_author(session, author_id)
    except AuthorNotFoundError as exec:
        raise HTTPException(status_code=404, detail=str(exec)) from exec
    
@app.post("/authors")
def create_author_endpoint(data: AuthorCreate, session: Session = Depends(get_session)):
    return create_author(session, data)

@app.patch("/authors/{author_id}")
def update_author_endpoint(author_id: int, data: AuthorUpdate, session: Session = Depends(get_session)):
    try:
        return update_author(session, author_id, data)
    except AuthorNotFoundError as exec:
        raise HTTPException(status_code=404, detail=str(exec)) from exec
    
@app.delete("/authors/{author_id}")
def delete_author_endpoint(author_id: int, session: Session = Depends(get_session)):
    try:
        return delete_author(session, author_id)
    except AuthorNotFoundError as exec:
        raise HTTPException(status_code=404, detail=str(exec)) from exec


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
