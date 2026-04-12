from fastmcp import FastMCP
from sqlmodel import Session

from app.db import create_db_and_tables, engine
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

mcp = FastMCP(name="LibraryMCPServer")
create_db_and_tables()


@mcp.tool()
def list_books_tool() -> list[dict]:
    """List all books in the catalog."""
    with Session(engine) as session:
        return [book.model_dump() for book in list_books(session)]


@mcp.tool()
def get_book_tool(book_id: int) -> dict:
    """Get a single book by id."""
    with Session(engine) as session:
        try:
            return get_book(session, book_id).model_dump()
        except BookNotFoundError as exc:
            return {"error": str(exc)}


@mcp.prompt()
def library_assistant_prompt(user_name: str = "User") -> str:
    """Prompt that configures the LLM as a library assistant."""
    return (
        f"You are a helpful library assistant helping {user_name}. "
        "Use the available tools to manage the catalog and answer questions about books. "
        "Prefer answers grounded in the catalog summary resource when possible."
    )


@mcp.tool()
def create_book_tool(title: str, author: str, year: int, available: bool = True) -> dict:
    """Create a new book in the catalog."""
    with Session(engine) as session:
        book = create_book(
            session,
            BookCreate(title=title, author=author, year=year, available=available),
        )
        return book.model_dump()


@mcp.tool()
def update_book_tool(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    available: bool | None = None,
) -> dict:
    """Update a book in the catalog."""
    with Session(engine) as session:
        try:
            book = update_book(
                session,
                book_id,
                BookUpdate(
                    title=title,
                    author=author,
                    year=year,
                    available=available,
                ),
            )
            return book.model_dump()
        except BookNotFoundError as exc:
            return {"error": str(exc)}


@mcp.tool()
def delete_book_tool(book_id: int) -> dict:
    """Delete a book from the catalog."""
    with Session(engine) as session:
        try:
            return delete_book(session, book_id)
        except BookNotFoundError as exc:
            return {"error": str(exc)}


@mcp.resource("library://catalog-summary")
def catalog_summary() -> str:
    """Return a plain-text summary of the current library catalog."""
    with Session(engine) as session:
        books = list_books(session)
        if not books:
            return "The library catalog is empty."
        return "\n".join(
            f"{book.id}: {book.title} by {book.author} ({book.year}) - available={book.available}"
            for book in books
        )

#Authors methods

@mcp.tool()
def list_authors_tool() -> list[dict]:
    """List all authors in the catalog."""
    with Session(engine) as session:
        return [author.model_dump() for author in list_authors(session)]
    
@mcp.tool()
def get_author_tool(author_id) -> dict:
    """Get a single author by id."""
    with Session(engine) as session:
        try:
            return get_author(session, author_id).model_dump()
        except AuthorNotFoundError as exc:
            return {"error": str(exc)}
        
@mcp.tool()
def create_author_tool(name: str, age: int, country: str) -> dict:
    """Create a new author in the catalog."""
    with Session(engine) as session:
        author = create_author(
            session,
            AuthorCreate(name=name, age=age, country=country),
        )
        return author.model_dump()


@mcp.tool()
def update_author_tool(
    author_id: int,
    name: str | None = None,
    age: int | None = None,
    country: str | None = None
) -> dict:
    """Update a author in the catalog."""
    with Session(engine) as session:
        try:
            author = update_author(
                session,
                author_id,
                AuthorUpdate(
                    name=name,
                    age=age,
                    country=country
                ),
            )
            return author.model_dump()
        except AuthorNotFoundError as exc:
            return {"error": str(exc)}


@mcp.tool()
def delete_author_tool(author_id: int) -> dict:
    """Delete a author from the catalog."""
    with Session(engine) as session:
        try:
            return delete_author(session, author_id)
        except AuthorNotFoundError as exc:
            return {"error": str(exc)}


@mcp.resource("library://authors-summary")
def authors_summary() -> str:
    """Return a plain-text summary of the current authors."""
    with Session(engine) as session:
        authors = list_authors(session)
        if not authors:
            return "There are no authors available."
        return "\n".join(
            f"{author.id}: {author.name} age {author.age} from ({author.country})"
            for author in authors
        )

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8002)
