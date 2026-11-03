from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birth_date = Column(Date)
    date_of_death = Column(Date)

    def __repr__(self):
        return f"Author (id = {self.id}, name = {self.name})"

class Book(db.Model):
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
        return f"Book (id = {self.id}, title = {self.title}, publication_year = {self.publication_year})"

