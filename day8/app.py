from flask import Flask, render_template
from flask import request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,login_required, logout_user, current_user

import os,sys
import click

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:  # if  Windows os
    prefix = 'sqlite:///'
else:  #  if not windows os
    prefix = 'sqlite:////'

app = Flask(__name__)
login_manager = LoginManager(app) 
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # close the model track
# db instance
db = SQLAlchemy(app)

class User(db.Model, UserMixin):  # table name is user（
    id = db.Column(db.Integer, primary_key=True)  # key
    name = db.Column(db.String(20))  # name
    username = db.Column(db.String(20))  # username
    password_hash = db.Column(db.String(128))  # passwprd hash 

    def set_password(self, password):  # password setting method
        self.password_hash = generate_password_hash(password)  # password sting hash generating

    def validate_password(self, password):  # valid password 
        return check_password_hash(self.password_hash, password)  # return boolean value

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # set password
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # set password
        db.session.add(user)

    db.session.commit()  # submit session
    click.echo('Done.')


class Book(db.Model):  # table name is Book
    id = db.Column(db.Integer, primary_key=True)  # key
    title = db.Column(db.String(60))  # book title
    year = db.Column(db.String(4))  # book year


@app.cli.command()  # command pass
@click.option('--drop', is_flag=True, help='Create after drop.')  # set options
def initdb(drop):
    """Initialize the database."""
    if drop:  # if option is drop
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # show hint information

@app.context_processor
def inject_user():  # you can change the function name
    user = User.query.first()
    return dict(user=user)  # return dict,is equal return {'user': user}

@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html', user=user), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # Verify that username and password match
        if username == user.username and user.validate_password(password):
            login_user(user)  # login user
            flash('Login success.')
            return redirect(url_for('index'))  # redirect to index page

        flash('Invalid username or password.')  # if validation is failure, and show error information
        return redirect(url_for('login'))  # redirect to login page

    return render_template('login.html')

@app.route('/logout')
@login_required  # view protect
def logout():
    logout_user()  # logou user
    flash('Goodbye.')
    return redirect(url_for('index'))  # redirect to index page

@login_manager.user_loader
def load_user(user_id):  # create user and load the load_user function to accpet the id as paramter 
    user = User.query.get(int(user_id))  # use id as user's primiary key to query user
    return user  # return user object

from flask import request, url_for, redirect, flash
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':  # detect if POST requirment
        # get form data
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')  #  name value in the form 
        year = request.form.get('year')
        # valide data
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # show the wrong information
            return redirect(url_for('index'))  # redirect to index
        # save the form data to database
        book = Book(title=title, year=year)  # create record
        db.session.add(book)  # add to database session
        db.session.commit()  # submit database session
        flash('Item created.')  #  show sucessful creating information
        return redirect(url_for('index'))  # redirect the index page

    books = Book.query.all()  # read all book record
    return render_template('index.html', books=books)

@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required 
def edit(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':  # process the edit form request
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=book_id))  # redirect to the edit page

        book.title = title  # update title
        book.year = year  #update year
        db.session.commit()  # submit db session
        flash('Item updated.')
        return redirect(url_for('index'))  # redirect to the index page

    return render_template('edit.html', book=book)  # pass the edited data

@app.route('/book/delete/<int:book_id>', methods=['POST'])  # 
@login_required 
def delete(book_id):
    book = Book.query.get_or_404(book_id)  # get book1 record1
    db.session.delete(book)  # delete the data
    db.session.commit()  # submit db session
    flash('Item deleted.')
    return redirect(url_for('index'))  # redirect to the index page

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user will return the login user data in the database.
        # same as following 
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    
    name = 'Tim'

    Books = [
        {'title': 'The Nickel Boys, Colson Whitehead', 'year': '2019'},
        {'title': 'Little Fires Everywhere, Celeste Ng', 'year': '2017'},
        {'title': 'Sing, Unburied Sing, Jesmyn Ward', 'year': '2017'},
        {'title': 'The Sellout, Paul Beatty', 'year': '2015'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Tenth of December, George Saunders', 'year': '2013'},
        {'title': 'Life After Life, Kate Atkinson', 'year': '2013'},
        {'title': 'Americanah, Chimamanda Ngozi Adichie', 'year': '2013'},
        {'title': 'Gone Girl, Gillian Flynn', 'year': '2012'},
        {'title': 'My Brilliant Friend, Elena Ferrante ', 'year': '2011'},
        {'title': 'A Visit From the Goon Squad, Jennifer Egan', 'year': '2010'}
    ]

    user = User(name=name)
    db.session.add(user)
    for m in Books:
        book = Book(title=m['title'], year=m['year'])
        db.session.add(book)

    db.session.commit()
    click.echo('Done.')

# name = 'Tim'

# Books = [
#     {'title': 'The Nickel Boys, Colson Whitehead', 'year': '2019'},
#     {'title': 'Little Fires Everywhere, Celeste Ng', 'year': '2017'},
#     {'title': 'Sing, Unburied Sing, Jesmyn Ward', 'year': '2017'},
#     {'title': 'The Sellout, Paul Beatty', 'year': '2015'},
#     {'title': 'Mahjong', 'year': '1996'},
#     {'title': 'Tenth of December, George Saunders', 'year': '2013'},
#     {'title': 'Life After Life, Kate Atkinson', 'year': '2013'},
#     {'title': 'Americanah, Chimamanda Ngozi Adichie', 'year': '2013'},
#     {'title': 'Gone Girl, Gillian Flynn', 'year': '2012'},
#     {'title': 'My Brilliant Friend, Elena Ferrante ', 'year': '2011'},
#      {'title': 'A Visit From the Goon Squad, Jennifer Egan', 'year': '2010'}
# ]

# @app.route('/')
# def index():
#     return render_template('index.html', name=name, books=Books)