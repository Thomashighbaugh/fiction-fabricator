import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey  # Add ForeignKey here
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
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

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))  # Foreign key to Book table
    title = Column(String)
    summary = Column(Text)
    content = Column(Text)  # Store the full chapter content

    book = relationship("Book", backref="chapters")  # Relationship for easier access


def create_database_if_not_exists(database_name):
    """
    Checks if a database exists and creates it if it doesn't.
    """

    if not os.path.isfile(database_name):
        create_database()
        print(f"Database '{database_name}' created.")
    else:
        print(f"Database '{database_name}' already exists.")


def create_database():
    engine = create_engine("sqlite:///books.db")
    Base.metadata.create_all(engine)


def save_book(book_data):
    engine = create_engine("sqlite:///books.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    book = Book(
        title=book_data["title"],
        genre=book_data["genre"],
        tone=book_data["tone"],
        style=book_data["style"],
        pov=book_data["pov"],
        premise=book_data["premise"],
        characters=json.dumps(book_data["characters"]),  # Convert to JSON
        chapters=json.dumps(book_data["chapters"]),     # Convert to JSON
    )

    session.add(book)

    # Create Chapter objects and link them to the Book
    for chapter_num, chapter_data in book_data["chapters"].items():
        chapter = Chapter(
            title=chapter_data["title"],
            summary=chapter_data["summary"],
            content="",  # You might want to store the final content here
            book=book,  # Associate the chapter with the book
        )
        session.add(chapter)

    session.commit()
    session.close()
    session.commit()
    session.close()


def load_book(book_id):
    engine = create_engine("sqlite:///books.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    book = session.query(Book).get(book_id)
    book.characters = json.loads(book.characters)  # Convert back to dictionary
    book.chapters = json.loads(book.chapters)      # Convert back to dictionary
    session.close()
    return book

def get_saved_projects():
    engine = create_engine("sqlite:///books.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    projects = session.query(Book.id, Book.title).all()
    session.close()
    return projects


