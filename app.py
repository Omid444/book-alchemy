from flask import Flask, request ,render_template, redirect, url_for, flash
from data_models import db, Author, Book
from datetime import datetime
import os

#os.makedirs("data", exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key' #it is used for flash
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
        for key in ['name', 'birth_date']:
            if not data.get(key) or data.get(key).strip() == '':
                return False, f"Field '{key}' must not be empty."
        date_format = "%Y-%m-%d"

        try:
            birth_validation = bool(datetime.strptime(data.get('birth_date'), date_format))
        except ValueError:
            return False, "Invalid birth_date format. Please use 'YYYY-MM-DD' format"
        date_of_death = data.get('date_of_death')
        if date_of_death.lower() == 'live':
            return True, None
        elif date_of_death.strip() == '':
            return True, None
        else:
            try:
                datetime.strptime(date_of_death, date_format)
            except ValueError:
                return False, "Invalid date_of_death format. Please use 'YYYY-MM-DD'."

        return True, None

    return False, "Unknown validation error."


def validate_params_book(data):
    required_keys = {'isbn', 'title', 'publication_year', 'author_id'}
    received_keys = set(request.values.keys())

    if received_keys > required_keys:
        extra = received_keys - required_keys
        return False, f"Unexpected parameter(s): {', '.join(extra)}"

    elif received_keys < required_keys:
        missing = required_keys - received_keys
        return False, f"Missing required parameter(s): {', '.join(missing)}"

    elif received_keys == required_keys:
        for key in required_keys:
            value = data.get(key)
            if not value or value.strip() == '':
                return False, f"Field '{key}' must not be empty."

        year_format = "%Y"
        try:
            datetime.strptime(data.get('publication_year'), year_format)
        except ValueError:
            return False, "Invalid publication_year format. Use 'YYYY' (e.g., '2004')."

        return True, None

    return False, "Unknown validation error."



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
            author = Author(name=name.lower(), birth_date=birth_date, date_of_death=date_of_death)
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
    authors = Author.query.all()
    print(authors)
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
            book = Book(isbn=isbn.lower(), title=title.lower(), publication_year=publication_year, author_id=author_id.lower())
            db.session.add(book)
            db.session.commit()
            return render_template('add_book.html', authors=authors, message=f'Book {title} successfully added to DB')

        else:
            return render_template('add_book.html',authors=authors, message=message_error)

    # if request is GET but there are extra params there
    if request.args:
        authors = Author.query.all()
        message_error = "Extra parameter are not allowed in GET request. please correct URL address"
        return render_template('add_book.html',authors=authors, message=message_error)

    return render_template('add_book.html',authors=authors)


@app.route('/',methods=['GET'])
def handle_home_page():
    message = ''
    sort = request.args.get('sort')
    search = request.args.get('search')
    if search:
        books = Book.query.filter(Book.title.ilike(f"%{search.lower()}%"))
        if not books.count() :
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
    book = db.session.get(Book, book_id)
    message = f'{book.title} deleted successfully from DB'
    author = db.session.get(Author, book.author_id)

    if book:
        db.session.delete(book)
        db.session.commit()
        authors_books = Author.query.get(book.author_id).books
        flash(message, 'success')
        if not authors_books:
            db.session.delete(author)
            db.session.commit()
    else:
        flash(f"{book.title} does not found")
    return redirect(url_for('handle_home_page'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)