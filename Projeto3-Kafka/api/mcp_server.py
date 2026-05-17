import traceback

from fastmcp import FastMCP
from sqlmodel import Session

from app.db import create_db_and_tables, engine
from app.models import BookCreate, BookUpdate, AuthorCreate, AuthorUpdate, CountryCreate, CountryUpdate
from app.services import (
    AuthorHasBooksError,
    AuthorNotFoundError,
    BookNotFoundError,
    CountryNotFoundError,
    create_author,
    create_author_from_text,
    create_book,
    delete_author,
    delete_book,
    get_author,
    get_book,
    list_authors,
    list_books,
    update_author,
    update_book,
    create_country,
    get_country,
    list_countries,
    update_country,
    delete_country,
    get_revenue_per_book,
    get_expenses_per_book,
    get_profit_per_book,
    get_total_revenue,
    get_total_expenses,
    get_total_profit,
    get_average_purchase_per_book,
    get_average_purchase_all_books,
    get_top_profit_book,
    get_revenue_last_hour,
    get_expenses_last_hour,
    get_profit_last_hour,
    get_top_country_sales_per_book,
)
from app.kafka_producer import get_producer

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
            print(f"MCP ERROR in get_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.prompt()
def library_assistant_prompt(user_name: str = "User") -> str:
    """Prompt that configures the LLM as a library assistant."""
    return (
        f"You are a helpful library assistant helping {user_name}. "
        "Use the available tools to manage the catalog and answer questions about books. "
        "Prefer answers grounded in the catalog summary resource when possible. "
        "When creating authors, use create_author_tool if the age is provided as a number, "
        "and use create_author_from_text_tool if the age is provided as text or quoted text."
    )


@mcp.tool()
def create_book_tool(title: str, author_id: int, year: int, available: bool = True) -> dict:
    """Create a new book in the catalog using an existing author id."""
    with Session(engine) as session:
        try:
            book = create_book(
                session,
                BookCreate(title=title, author_id=author_id, year=year, available=available),
            )
            return book.model_dump()
        except (AuthorNotFoundError, ValueError) as exc:
            print(f" MCP ERROR in create_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def update_book_tool(
    book_id: int,
    title: str | None = None,
    author_id: int | None = None,
    year: int | None = None,
    available: bool | None = None,
) -> dict:
    """Update a book in the catalog, including changing its linked author."""
    with Session(engine) as session:
        try:
            book = update_book(
                session,
                book_id,
                BookUpdate(
                    title=title,
                    author_id=author_id,
                    year=year,
                    available=available,
                ),
            )
            return book.model_dump()
        except (BookNotFoundError, AuthorNotFoundError, ValueError) as exc:
            print(f" MCP ERROR in update_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def delete_book_tool(book_id: int) -> dict:
    """Delete a book from the catalog."""
    with Session(engine) as session:
        try:
            return delete_book(session, book_id)
        except BookNotFoundError as exc:
            print(f"MCP ERROR in delete_book_tool: {exc}")
            traceback.print_exc()
            raise


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
def get_author_tool(author_id: int) -> dict:
    """Get a single author by id."""
    with Session(engine) as session:
        try:
            return get_author(session, author_id).model_dump()
        except AuthorNotFoundError as exc:
            print(f"MCP ERROR in get_author_tool: {exc}")
            traceback.print_exc()
            raise
        
@mcp.tool()
def create_author_tool(name: str, age: int, country: str) -> dict:
    """Create a new author in the catalog using an integer age."""
    with Session(engine) as session:
        author = create_author(
            session,
            AuthorCreate(name=name, age=age, country=country),
        )
        return author.model_dump()


@mcp.tool()
def create_author_from_text_tool(name: str, age_text: str, country: str) -> dict:
    """Create a new author in the catalog using age as text."""
    with Session(engine) as session:
        try:
            return create_author_from_text(session, name=name, age_text=age_text, country=country)
        except ValueError as exc:
            print(f"MCP ERROR in create_author_from_text_tool: {exc}")
            traceback.print_exc()
            raise


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
            print(f"MCP ERROR in update_author_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def delete_author_tool(author_id: int) -> dict:
    """Delete an author from the catalog."""
    with Session(engine) as session:
        try:
            return delete_author(session, author_id)
        except (AuthorNotFoundError, AuthorHasBooksError) as exc:
            print(f" MCP ERROR in delete_author_tool: {exc}")
            traceback.print_exc()
            raise


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


# Country CRUD Tools (for assignment requirements #1-2)

@mcp.tool()
def list_countries_tool() -> list[dict]:
    """List all countries in the database. Requirement #2: List countries."""
    with Session(engine) as session:
        return [country.model_dump() for country in list_countries(session)]


@mcp.tool()
def get_country_tool(country_id: int) -> dict:
    """Get a single country by id."""
    with Session(engine) as session:
        try:
            return get_country(session, country_id).model_dump()
        except CountryNotFoundError as exc:
            print(f"MCP ERROR in get_country_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def create_country_tool(name: str, region: str) -> dict:
    """Create a new country. Requirement #1: Add countries to the database."""
    with Session(engine) as session:
        try:
            country = create_country(
                session,
                CountryCreate(name=name, region=region),
            )
            return country.model_dump()
        except ValueError as exc:
            print(f"MCP ERROR in create_country_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def update_country_tool(
    country_id: int,
    name: str | None = None,
    region: str | None = None,
) -> dict:
    """Update a country in the database."""
    with Session(engine) as session:
        try:
            country = update_country(
                session,
                country_id,
                CountryUpdate(name=name, region=region),
            )
            return country.model_dump()
        except CountryNotFoundError as exc:
            print(f"MCP ERROR in update_country_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def delete_country_tool(country_id: int) -> dict:
    """Delete a country from the database."""
    with Session(engine) as session:
        try:
            return delete_country(session, country_id)
        except CountryNotFoundError as exc:
            print(f"MCP ERROR in delete_country_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.resource("library://countries-summary")
def countries_summary() -> str:
    """Return a plain-text summary of countries in the database."""
    with Session(engine) as session:
        countries = list_countries(session)
        if not countries:
            return "There are no countries in the database."
        return "\n".join(
            f"{country.id}: {country.name} ({country.region})"
            for country in countries
        )


# ===== ANALYTICS TOOLS (Requirements #5-17) =====

@mcp.tool()
def get_revenue_per_book_tool() -> list[dict]:
    """Get revenue per book computed by Kafka Streams. Requirement #5: Revenue per item."""
    with Session(engine) as session:
        try:
            return get_revenue_per_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_revenue_per_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_expenses_per_book_tool() -> list[dict]:
    """Get expenses per book computed by Kafka Streams. Requirement #6: Expenses per item."""
    with Session(engine) as session:
        try:
            return get_expenses_per_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_expenses_per_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_profit_per_book_tool() -> list[dict]:
    """Get profit per book computed by Kafka Streams. Requirement #7: Profit per item."""
    with Session(engine) as session:
        try:
            return get_profit_per_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_profit_per_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_total_revenue_tool() -> dict:
    """Get total revenue computed by Kafka Streams. Requirement #8: Total revenue."""
    with Session(engine) as session:
        try:
            return get_total_revenue(session)
        except Exception as exc:
            print(f"MCP ERROR in get_total_revenue_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_total_expenses_tool() -> dict:
    """Get total expenses computed by Kafka Streams. Requirement #9: Total expenses."""
    with Session(engine) as session:
        try:
            return get_total_expenses(session)
        except Exception as exc:
            print(f"MCP ERROR in get_total_expenses_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_total_profit_tool() -> dict:
    """Get total profit computed by Kafka Streams. Requirement #10: Total profit."""
    with Session(engine) as session:
        try:
            return get_total_profit(session)
        except Exception as exc:
            print(f"MCP ERROR in get_total_profit_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_average_purchase_per_book_tool() -> list[dict]:
    """Get average purchase per book computed by Kafka Streams. Requirement #11: Avg purchase per item."""
    with Session(engine) as session:
        try:
            return get_average_purchase_per_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_average_purchase_per_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_average_purchase_all_books_tool() -> dict:
    """Get average purchase across all books computed by Kafka Streams. Requirement #12: Avg purchase all items."""
    with Session(engine) as session:
        try:
            return get_average_purchase_all_books(session)
        except Exception as exc:
            print(f"MCP ERROR in get_average_purchase_all_books_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_top_profit_book_tool() -> dict:
    """Get top profit book computed by Kafka Streams. Requirement #13: Top profit item."""
    with Session(engine) as session:
        try:
            return get_top_profit_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_top_profit_book_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_revenue_last_hour_tool() -> dict:
    """Get revenue in last hour computed by Kafka Streams. Requirement #14: Revenue last hour."""
    with Session(engine) as session:
        try:
            return get_revenue_last_hour(session)
        except Exception as exc:
            print(f"MCP ERROR in get_revenue_last_hour_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_expenses_last_hour_tool() -> dict:
    """Get expenses in last hour computed by Kafka Streams. Requirement #15: Expenses last hour."""
    with Session(engine) as session:
        try:
            return get_expenses_last_hour(session)
        except Exception as exc:
            print(f"MCP ERROR in get_expenses_last_hour_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_profit_last_hour_tool() -> dict:
    """Get profit in last hour computed by Kafka Streams. Requirement #16: Profit last hour."""
    with Session(engine) as session:
        try:
            return get_profit_last_hour(session)
        except Exception as exc:
            print(f"MCP ERROR in get_profit_last_hour_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_profit_last_hour_tool() -> dict:
    """Get profit in last hour computed by Kafka Streams. Requirement #16: Profit last hour."""
    with Session(engine) as session:
        try:
            return get_profit_last_hour(session)
        except Exception as exc:
            print(f"MCP ERROR in get_profit_last_hour_tool: {exc}")
            traceback.print_exc()
            raise


@mcp.tool()
def get_top_country_sales_per_book_tool() -> list[dict]:
    """Get country with highest sales per book computed by Kafka Streams. Requirement #17: Top sales by country per item."""
    with Session(engine) as session:
        try:
            return get_top_country_sales_per_book(session)
        except Exception as exc:
            print(f"MCP ERROR in get_top_country_sales_per_book_tool: {exc}")
            traceback.print_exc()
            raise


# ===== KAFKA PRODUCER TOOLS =====

@mcp.tool()
def create_purchase_event(book_id: int, supplier_id: int, cost: float, quantity: int) -> dict:
    """Create a purchase order event and send to Kafka. Simulates a supplier delivering books."""
    try:
        producer = get_producer()
        return producer.send_purchase_event(book_id, supplier_id, cost, quantity)
    except Exception as exc:
        print(f"MCP ERROR in create_purchase_event: {exc}")
        traceback.print_exc()
        return {"status": "error", "message": str(exc)}


@mcp.tool()
def create_sale_event(book_id: int, country_id: int, price: float, quantity: int) -> dict:
    """Create a sale event and send to Kafka. Simulates customers buying books."""
    try:
        producer = get_producer()
        return producer.send_sale_event(book_id, country_id, price, quantity)
    except Exception as exc:
        print(f"MCP ERROR in create_sale_event: {exc}")
        traceback.print_exc()
        return {"status": "error", "message": str(exc)}


@mcp.tool()
def create_test_transactions(num_purchases: int = 5, num_sales: int = 5) -> dict:
    """Create random test transactions (purchases and sales) to populate Kafka topics."""
    import random

    producer = get_producer()

    # Generate random test data
    book_ids = [1, 2, 3, 4, 5]
    country_ids = [1, 2, 3]
    supplier_ids = [10, 11, 12]

    purchases = [
        {
            "book_id": random.choice(book_ids),
            "supplier_id": random.choice(supplier_ids),
            "cost": round(random.uniform(3.0, 10.0), 2),
            "quantity": random.randint(1, 20)
        }
        for _ in range(num_purchases)
    ]

    sales = [
        {
            "book_id": random.choice(book_ids),
            "country_id": random.choice(country_ids),
            "price": round(random.uniform(12.0, 25.0), 2),
            "quantity": random.randint(1, 10)
        }
        for _ in range(num_sales)
    ]

    purchase_results = producer.send_purchase_events_batch(purchases)
    sale_results = producer.send_sale_events_batch(sales)

    return {
        "status": "success",
        "message": f"Created {num_purchases} purchases and {num_sales} sales",
        "purchases": purchase_results,
        "sales": sale_results
    }


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8002)
