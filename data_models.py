"""SQLAlchemy models for authors and books in the library."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date

db = SQLAlchemy()

# pylint: disable=too-few-public-methods
class Author(db.Model):
    """Represent an author stored in the library database."""

    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birth_date = Column(Date)
    date_of_death = Column(Date)

    def __repr__(self):
        """Return a developer-friendly representation of the author."""
        return f"Author (id = {self.id}, name = {self.name})"

# pylint: disable=too-few-public-methods
class Book(db.Model):
    """Represent a book and its relationship to an author."""

    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String)
    title = Column(String)
    publication_year = Column(String)

    author_id = Column(Integer, db.ForeignKey('authors.id'))
    rating = db.Column(db.Integer, nullable=True)

    author = db.relationship(
        "Author",
        backref=db.backref(
            "books",
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        """Return a developer-friendly representation of the book."""
        return (
            f"Book (id = {self.id}, title = {self.title}, "
            f"publication_year = {self.publication_year})"
        )
