from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INTEGER, Float, String, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'author'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    date_of_death = Column(String, nullable=False)


    def __repr__(self):
        return f"id: {Author.id}, {Author.name} {Author.birth_date}  {Author.date_of_death}"


class Book(db.Model):
    __tablename__ = 'book'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    publication_year = Column(String, nullable=False)
    author_id = Column(INTEGER, ForeignKey("author.id") )


    def __repr__(self):
        return f"id: {Book.id}, {Book.isbn} {Book.title} {Book.publication_year} {Book.author_id}"