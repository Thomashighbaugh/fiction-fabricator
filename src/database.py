import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    tone = Column(String)
    style = Column(String)
    pov = Column(String)
    premise = Column(Text)
    characters = Column(Text)
    chapters = Column(Text)


def create_database_if_not_exists(database_name):
    """
    Checks if a database exists and creates it if it doesn't.
    """

    if not os.path.isfile(database_name):  # Check if the database file exists
        create_database()  # Create the database and tables
        print(f"Database '{database_name}' created.")
    else:
        print(f"Database '{database_name}' already exists.")


def create_database():
    engine = create_engine("sqlite:///books.db")  # Create or connect to the database
    Base.metadata.create_all(engine)  # Create tables if they don't exist


def save_book(book_data):
    engine = create_engine("sqlite:///books.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a Book object and populate it with data
    book = Book(
        title=book_data[0],
        genre=book_data[1],
        tone=book_data[2],
        style=book_data[3],
        pov=book_data[4],
        premise=book_data[5],
        characters=book_data[6],
        chapters=book_data[7],
    )

    session.add(book)  # Add the book to the session
    session.commit()  # Save changes to the database
    session.close()


def load_book(book_id):
    engine = create_engine("sqlite:///books.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query for the book with the given ID
    book = session.query(Book).get(book_id)

    session.close()
    return book
