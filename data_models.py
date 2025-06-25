from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INTEGER, Float, String, DATE
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'author'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    date_of_death = Column(String, nullable=False)


    def __str__(self):
        return f"id: {Author.id}, {Author.name} {Author.birth_date}  {Author.date_of_death}"