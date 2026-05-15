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


# ===== ANALYTICS FUNCTIONS (Requirements #5-17) =====

def get_revenue_per_book(session: Session) -> list[dict]:
    """Query revenue_by_book table computed by Kafka Streams. Requirement #5."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT * FROM revenue_by_book ORDER BY revenue DESC")).all()
        return [{"book_id": int(r[0]), "revenue": float(r[1])} for r in result]
    except Exception as e:
        # Table might not exist yet if Kafka hasn't processed events
        return [{"error": f"Cannot query revenue_by_book: {str(e)}"}]


def get_expenses_per_book(session: Session) -> list[dict]:
    """Query expenses_by_book table computed by Kafka Streams. Requirement #6."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT * FROM expenses_by_book ORDER BY expenses DESC")).all()
        return [{"book_id": int(r[0]), "expenses": float(r[1])} for r in result]
    except Exception as e:
        return [{"error": f"Cannot query expenses_by_book: {str(e)}"}]


def get_profit_per_book(session: Session) -> list[dict]:
    """Query profit_by_book table computed by Kafka Streams. Requirement #7."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT * FROM profit_by_book ORDER BY profit DESC")).all()
        return [{"book_id": int(r[0]), "profit": float(r[1])} for r in result]
    except Exception as e:
        return [{"error": f"Cannot query profit_by_book: {str(e)}"}]


def get_total_revenue(session: Session) -> dict:
    """Query total_revenue from total_metrics table computed by Kafka Streams. Requirement #8."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM total_metrics WHERE metric_name = 'total_revenue'")).first()
        if result:
            return {"total_revenue": float(result[0])}
        return {"total_revenue": 0.0}
    except Exception as e:
        return {"error": f"Cannot query total_revenue: {str(e)}"}


def get_total_expenses(session: Session) -> dict:
    """Query total_expenses from total_metrics table computed by Kafka Streams. Requirement #9."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM total_metrics WHERE metric_name = 'total_expenses'")).first()
        if result:
            return {"total_expenses": float(result[0])}
        return {"total_expenses": 0.0}
    except Exception as e:
        return {"error": f"Cannot query total_expenses: {str(e)}"}


def get_total_profit(session: Session) -> dict:
    """Query total_profit from total_metrics table computed by Kafka Streams. Requirement #10."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM total_metrics WHERE metric_name = 'total_profit'")).first()
        if result:
            return {"total_profit": float(result[0])}
        return {"total_profit": 0.0}
    except Exception as e:
        return {"error": f"Cannot query total_profit: {str(e)}"}


def get_average_purchase_per_book(session: Session) -> list[dict]:
    """Query average_purchase_by_book table computed by Kafka Streams. Requirement #11."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT book_id, average_amount FROM average_purchase_by_book ORDER BY average_amount DESC")).all()
        return [{"book_id": int(r[0]), "avg_purchase": float(r[1])} for r in result]
    except Exception as e:
        return [{"error": f"Cannot query average_purchase_by_book: {str(e)}"}]


def get_average_purchase_all_books(session: Session) -> dict:
    """Query average_purchase from total_metrics table computed by Kafka Streams. Requirement #12."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM total_metrics WHERE metric_name = 'average_purchase'")).first()
        if result:
            return {"average_purchase": float(result[0])}
        return {"average_purchase": 0.0}
    except Exception as e:
        return {"error": f"Cannot query average_purchase: {str(e)}"}


def get_top_profit_book(session: Session) -> dict:
    """Query top_profit_book from total_metrics table computed by Kafka Streams. Requirement #13."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM total_metrics WHERE metric_name = 'top_profit_book'")).first()
        if result:
            return {"profit": float(result[0])}
        return {"error": "No data available"}
    except Exception as e:
        return {"error": f"Cannot query top_profit_book: {str(e)}"}


def get_revenue_last_hour(session: Session) -> dict:
    """Query revenue_last_hour from time_window_metrics table. Requirement #14."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM time_window_metrics WHERE metric_type = 'revenue_last_hour'")).first()
        if result:
            return {"revenue_last_hour": float(result[0])}
        return {"revenue_last_hour": 0.0}
    except Exception as e:
        return {"error": f"Cannot query revenue_last_hour: {str(e)}"}


def get_expenses_last_hour(session: Session) -> dict:
    """Query expenses_last_hour from time_window_metrics table. Requirement #15."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM time_window_metrics WHERE metric_type = 'expenses_last_hour'")).first()
        if result:
            return {"expenses_last_hour": float(result[0])}
        return {"expenses_last_hour": 0.0}
    except Exception as e:
        return {"error": f"Cannot query expenses_last_hour: {str(e)}"}


def get_profit_last_hour(session: Session) -> dict:
    """Query profit_last_hour from time_window_metrics table. Requirement #16."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT metric_value FROM time_window_metrics WHERE metric_type = 'profit_last_hour'")).first()
        if result:
            return {"profit_last_hour": float(result[0])}
        return {"profit_last_hour": 0.0}
    except Exception as e:
        return {"error": f"Cannot query profit_last_hour: {str(e)}"}


def get_top_country_sales_per_book(session: Session) -> list[dict]:
    """Query best_performing_by_country table computed by Kafka Streams. Requirement #17."""
    from sqlalchemy import text

    try:
        result = session.exec(text("SELECT book_id, country_id, sales_volume, revenue FROM best_performing_by_country ORDER BY revenue DESC")).all()
        return [{"book_id": int(r[0]), "country_id": int(r[1]), "sales_volume": float(r[2]) if r[2] else 0.0, "revenue": float(r[3]) if r[3] else 0.0} for r in result]
    except Exception as e:
        return [{"error": f"Cannot query best_performing_by_country: {str(e)}"}]