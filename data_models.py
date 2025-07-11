from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INTEGER, Float, String, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'author'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    date_of_death = Column(String, nullable=True)
    books = relationship('Book', back_populates='author')

    def __repr__(self):
        return f"id: {self.id}, {self.name} {self.birth_date}  {self.date_of_death}"


class Book(db.Model):
    __tablename__ = 'book'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    publication_year = Column(String, nullable=False)
    author_id = Column(INTEGER, ForeignKey("author.id") , nullable=False)
    author = relationship('Author', back_populates='books', lazy='joined')


    def __repr__(self):
        return f"id: {self.id}, {self.isbn} {self.title} {self.publication_year} {self.author_id}"