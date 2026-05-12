from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///library.db"
engine = create_engine(DATABASE_URL, echo=False)


def _migrate_book_table() -> None:
    with engine.begin() as connection:
        columns = connection.exec_driver_sql("PRAGMA table_info(book)").fetchall()
        if not columns:
            return

        column_names = {column[1] for column in columns}
        if "author_id" not in column_names:
            connection.exec_driver_sql("ALTER TABLE book ADD COLUMN author_id INTEGER")
            connection.exec_driver_sql(
                """
                UPDATE book
                SET author_id = (
                    SELECT author.id
                    FROM author
                    WHERE author.name = book.author
                    LIMIT 1
                )
                WHERE author_id IS NULL
                """
            )


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate_book_table()


def get_session():
    with Session(engine) as session:
        yield session
