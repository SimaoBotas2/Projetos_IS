from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from app.db import create_db_and_tables, get_session
from app.models import (
    BookCreate, BookUpdate, AuthorCreate, AuthorUpdate,
    CountryCreate, CountryUpdate
)
from app.services import (
    AuthorHasBooksError,
    AuthorNotFoundError,
    BookNotFoundError,
    CountryNotFoundError,
    create_author,
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
    list_countries,
    get_country,
    update_country,
    delete_country,
)

app = FastAPI(title="Library REST API")

#
@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/")
def read_root():
    return {
        "message": "Library and Analytics REST API is running",
        "library_endpoints": [
            "GET /books", "GET /books/{id}", "POST /books", "PATCH /books/{id}", "DELETE /books/{id}", 
            "GET /authors", "GET /authors/{id}", "POST /authors", "PATCH /authors/{id}", "DELETE /authors/{id}",
        ],
        "analytics_endpoints": [
            "GET /analytics/countries", "POST /analytics/countries",
            "GET /analytics/items", "POST /analytics/items",
            "GET /analytics/stats/revenue-per-item",
            "GET /analytics/stats/expenses-per-item",
            "GET /analytics/stats/profit-per-item",
            "GET /analytics/stats/total-revenue",
            "GET /analytics/stats/total-expenses",
            "GET /analytics/stats/total-profit",
            "GET /analytics/stats/average-purchase-per-item",
            "GET /analytics/stats/average-purchase-all-items",
            "GET /analytics/stats/top-profit-item",
            "GET /analytics/stats/revenue-last-hour",
            "GET /analytics/stats/expenses-last-hour",
            "GET /analytics/stats/profit-last-hour",
            "GET /analytics/stats/top-country-sales-per-item",
            "GET /analytics/stats/dashboard",
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
    try:
        return create_book(session, data)
    except (AuthorNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.patch("/books/{book_id}")
def update_book_endpoint(
    book_id: int, data: BookUpdate, session: Session = Depends(get_session)
):
    try:
        return update_book(session, book_id, data)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (AuthorNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    except AuthorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
@app.post("/authors")
def create_author_endpoint(data: AuthorCreate, session: Session = Depends(get_session)):
    return create_author(session, data)

@app.patch("/authors/{author_id}")
def update_author_endpoint(author_id: int, data: AuthorUpdate, session: Session = Depends(get_session)):
    try:
        return update_author(session, author_id, data)
    except AuthorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
@app.delete("/authors/{author_id}")
def delete_author_endpoint(author_id: int, session: Session = Depends(get_session)):
    try:
        return delete_author(session, author_id)
    except AuthorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AuthorHasBooksError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# Country CRUD endpoints
@app.get("/countries")
def read_countries(session: Session = Depends(get_session)):
    return list_countries(session)


@app.get("/countries/{country_id}")
def read_country(country_id: int, session: Session = Depends(get_session)):
    try:
        return get_country(session, country_id)
    except CountryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/countries")
def create_country_endpoint(data: CountryCreate, session: Session = Depends(get_session)):
    return create_country(session, data)


@app.patch("/countries/{country_id}")
def update_country_endpoint(country_id: int, data: CountryUpdate, session: Session = Depends(get_session)):
    try:
        return update_country(session, country_id, data)
    except CountryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/countries/{country_id}")
def delete_country_endpoint(country_id: int, session: Session = Depends(get_session)):
    try:
        return delete_country(session, country_id)
    except CountryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Analytics Stats endpoints
# These will eventually be populated from Kafka Streams results
# For now, they return placeholder messages
@app.get("/analytics/stats/revenue-per-book")
def get_revenue_per_book():
    return {"message": "Revenue per book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/expenses-per-book")
def get_expenses_per_book():
    return {"message": "Expenses per book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/profit-per-book")
def get_profit_per_book():
    return {"message": "Profit per book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/total-revenue")
def get_total_revenue():
    return {"message": "Total revenue (computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/total-expenses")
def get_total_expenses():
    return {"message": "Total expenses (computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/total-profit")
def get_total_profit():
    return {"message": "Total profit (computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/average-purchase-per-book")
def get_average_purchase_per_book():
    return {"message": "Average purchase per book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/average-purchase-all-books")
def get_average_purchase_all_books():
    return {"message": "Average purchase across all books (computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/top-profit-book")
def get_top_profit_book():
    return {"message": "Top profit book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/revenue-last-hour")
def get_revenue_last_hour():
    return {"message": "Revenue in last hour (time-windowed, computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/expenses-last-hour")
def get_expenses_last_hour():
    return {"message": "Expenses in last hour (time-windowed, computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/profit-last-hour")
def get_profit_last_hour():
    return {"message": "Profit in last hour (time-windowed, computed by Kafka Streams)", "value": 0}


@app.get("/analytics/stats/top-country-sales-per-book")
def get_top_country_sales_per_book():
    return {"message": "Country with highest sales per book (computed by Kafka Streams)", "data": {}}


@app.get("/analytics/stats/dashboard")
def get_dashboard_summary():
    return {
        "message": "Dashboard summary - aggregated analytics results",
        "data": {
            "total_revenue": 0,
            "total_expenses": 0,
            "total_profit": 0,
            "average_purchase": 0,
            "top_profit_item": {},
            "top_profit_item_last_hour": {},
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
