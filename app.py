from flask import Flask, request
from data_models import db, Author, Book
from flask_sqlalchemy import SQLAlchemy
import os

#os.makedirs("data", exist_ok=True)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "library.sqlite")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

# with app.app_context():
#   db.create_all()


@app.route('/add_author',Methods=['GET','POST'])
def handle_add_book():
    if request.method == 'POST':









if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)