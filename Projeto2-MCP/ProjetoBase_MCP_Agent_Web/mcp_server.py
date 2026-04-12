from fastmcp import FastMCP
from sqlmodel import Session

from app.db import create_db_and_tables, engine
from app.models import BookCreate, BookUpdate
from app.services import (
    BookNotFoundError,
    create_book,
    delete_book,
    get_book,
    list_books,
    update_book,
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


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8002)
