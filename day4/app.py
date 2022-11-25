from flask import Flask, render_template

app = Flask(__name__)

name = 'Time'

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

@app.route('/')
def index():
    return render_template('index.html', name=name, books=Books)