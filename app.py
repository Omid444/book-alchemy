from flask import Flask, request ,render_template
from data_models import db, Author, Book
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

#os.makedirs("data", exist_ok=True)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "library.sqlite")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

# with app.app_context():
#    db.create_all()

def validate_params(required_keys, received_keys, received_values):

    message_error = "Parameter should not be left empty"

    if received_keys > required_keys :
        extra = received_keys - required_keys
        return False, f"Unexpected parameter(s): {', '.join(extra)}"

    elif received_keys < required_keys:
        missing = required_keys - required_keys
        return False, f"Missing required parameter(s): {missing}"

    elif received_keys == required_keys:
        date_format = "%d-%m-%Y"
        try:
            birth_validation = bool(datetime.strptime(received_values[1], date_format))
        except ValueError:
            message_error = "Invalid birth_date format, please write valid format '%d-%m-%Y'"
            birth_validation = False
        try:
            if received_values[2] == 'live' or received_values[2] =='':
                death_validation = True
            else:
                death_validation = bool(datetime.strptime(received_values[2], date_format))
        except ValueError:
            message_error = "Invalid date_of_death format, please write valid format '%d-%m-%Y'"
            death_validation = False
        if all(received_keys) and birth_validation and death_validation:
            return True , None

        return False, message_error






@app.route('/add_author', methods=['GET','POST'])
def handle_add_author():
    if request.method == 'POST':

        required_keys = {'name', 'birth_date', 'date_of_death'}
        received_keys = set(request.values.keys())
        received_values = list(request.values.values())
        data_validation, message_error = validate_params(required_keys, received_keys, received_values)
        print(data_validation, message_error)
        print(received_keys, received_values)
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
        title = request.values.get('title')
        isbn = request.values.get('isbn')
        publication_year = request.values.get('publication_year')












if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)