from sqlmodel import Session, SQLModel, create_engine

# PostgreSQL connection to Kafka project database
DATABASE_URL = "postgresql+psycopg://postgres:nopass@localhost:5432/project3"
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Create tables. PostgreSQL schema is managed by Kafka Connect."""
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
