from app.db import engine
from app.models import Author, Book, Country
from sqlmodel import Session

def seed_database():
    """Insert sample data for testing"""
    with Session(engine) as session:
        # Create 3 countries
        countries = [
            Country(name="Portugal", region="Europe"),
            Country(name="Spain", region="Europe"),
            Country(name="France", region="Europe"),
        ]
        session.add_all(countries)
        session.commit()

        # Create 3 authors
        authors = [
            Author(name="Jose Saramago", age=88, country="Portugal"),
            Author(name="Gabriel Garcia Marquez", age=87, country="Colombia"),
            Author(name="Victor Hugo", age=85, country="France"),
        ]
        session.add_all(authors)
        session.commit()

        # Create 5 books (linked to authors)
        books = [
            Book(title="Ensaio sobre a Cegueira", year=1995, author="Jose Saramago",
                 author_id=authors[0].id, available=True, cost_price=5.0, sale_price=15.0),
            Book(title="Cien anos de soledad", year=1967, author="Gabriel Garcia Marquez",
                 author_id=authors[1].id, available=True, cost_price=8.0, sale_price=18.0),
            Book(title="Les Miserables", year=1862, author="Victor Hugo",
                 author_id=authors[2].id, available=True, cost_price=6.0, sale_price=16.0),
            Book(title="O Evangelho Segundo Jesus Cristo", year=1991, author="Jose Saramago",
                 author_id=authors[0].id, available=True, cost_price=5.5, sale_price=14.0),
            Book(title="Amor em tempos de colera", year=1985, author="Gabriel Garcia Marquez",
                 author_id=authors[1].id, available=True, cost_price=7.0, sale_price=17.0),
        ]
        session.add_all(books)
        session.commit()

        print("Created 3 countries")
        print("Created 3 authors")
        print("Created 5 books")
        print("\nDatabase seeded successfully!")

if __name__ == "__main__":
    seed_database()
