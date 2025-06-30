from flask import Flask, request ,render_template, redirect, url_for
from data_models import db, Author, Book
from datetime import datetime
import os

#os.makedirs("data", exist_ok=True)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "library.sqlite")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

# with app.app_context():
#   db.create_all()

def validate_params_author(data):
    message_error = "Parameter should not be left empty. For a live author, write 'live' in date_of_death"
    required_keys = {'name', 'birth_date', 'date_of_death'}
    received_keys = set(data.keys())

    print('line 24',received_keys, data.keys(), data.get('name'))

    if received_keys > required_keys:
        extra = received_keys - required_keys
        return False, f"Unexpected parameter(s): {', '.join(extra)}"

    elif received_keys < required_keys:
        missing = required_keys - received_keys
        return False, f"Missing required parameter(s): {', '.join(missing)}"

    elif received_keys == required_keys:
        date_format = "%Y-%m-%d"

        try:
            birth_validation = bool(datetime.strptime(data.get('birth_date'), date_format))
        except ValueError:
            return False, "Invalid birth_date format. Please use 'YYYY-MM-DD' format"

        try:
            date_of_death = data.get('date_of_death')
            if date_of_death in ('', 'live'):
                death_validation = True
            else:
                death_validation = bool(datetime.strptime(date_of_death, date_format))
        except ValueError:
            return False, "Invalid date_of_death format. Please use 'YYYY-MM-DD' format"

        if birth_validation and death_validation:
            return True, None

        return False, message_error
    return False, "Unknown validation error"


def validate_params_book(data):

    message_error = "Parameter should not be left empty"
    required_keys = {'isbn', 'title', 'publication_year', 'author_id'}
    received_keys = set(request.values.keys())
    print(received_keys)
    if received_keys > required_keys :
        extra = received_keys - required_keys
        return False, f"Unexpected parameter(s): {', '.join(extra)}"

    elif received_keys < required_keys:
        missing = required_keys - received_keys
        return False, f"Missing required parameter(s): {','.join(missing)}"

    elif received_keys == required_keys:
        year_format = "%Y"
        try:
            publication_validation = bool(datetime.strptime(data.get('publication_year'), year_format))
        except ValueError:
            message_error = ("Invalid publication_year format or empty block , "
                             "please write valid format e.g.'2004' and fill all required field")
            return False, message_error
        if all(request.values.values()) and publication_validation:
            return True, None

        return False, message_error
    return False, "Unknown validation error"



@app.route('/add_author', methods=['GET','POST'])
def handle_add_author():
    if request.method == 'POST':
        print('request value',request.values)
        data_validation, message_error = validate_params_author(request.values)
        print('data validation',data_validation, message_error)
        if data_validation:
            name = request.values.get('name')
            birth_date = request.values.get('birth_date')
            date_of_death = None if request.values.get('date_of_death') == '' or request.values.get('date_of_death') == 'live' else request.values.get('date_of_death')
            print(name, birth_date, date_of_death)
            author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(author)
            db.session.commit()
            return render_template('add_author.html', message = f'Author {name} successfully added to DB')

        else:
            return render_template('add_author.html', message = message_error)

    #if request is GET but there are extra params there
    if request.args:
        message_error = "Extra parameter are not allowed in GET request. please correct URL address"
        return render_template('add_author.html', message=message_error)

    return render_template('add_author.html')


@app.route('/add_book',methods=['GET','POST'])
def handle_add_book():
    if request.method == 'POST':
        print(request.values)
        data_validation, message_error = validate_params_book(request.values)
        print(data_validation, message_error)
        if data_validation:
            isbn = request.values.get('isbn')
            title = request.values.get('title')
            publication_year = request.values.get('publication_year')
            author_id = request.values.get('author_id')
            print(isbn, title, publication_year)
            book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(book)
            db.session.commit()
            return render_template('add_book.html', message=f'Book {title} successfully added to DB')

        else:
            return render_template('add_book.html', message=message_error)

    # if request is GET but there are extra params there
    if request.args:
        message_error = "Extra parameter are not allowed in GET request. please correct URL address"
        return render_template('add_book.html', message=message_error)

    return render_template('add_book.html')


@app.route('/',methods=['GET'])
def handle_home_page():
    message = ''
    sort = request.args.get('sort')
    search = request.args.get('search')
    if search:
        books = Book.query.filter(Book.title.ilike(f"%{search.lower()}%"))
        print(books)
        if search not in books:
            message = f'No book found with such title: {search}'
    elif sort == 'title':
        books = Book.query.order_by(Book.title).all()
    elif sort == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.all()

    return render_template('home.html', books=books, message=message)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def handle_delete_book(book_id):
    book = Book.query.get(book_id)
    message = f'{book} deleted successfully from DB'
    #author_id = Book.author_id if Book.query.filter(Book.id == book_id) else ''
    #author = Author.query.filter(Author.id == book)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('handle_home_page'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)