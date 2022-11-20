from flask import Flask
from markupsafe import escape
from flask import url_for

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello Totoro!</h1><img src="https://www.boredpanda.com/blog/wp-content/uploads/2016/07/totoro-exercising-100-days-of-gifs-cl-terryart-2-578f80ec7f328__605.gif">'

@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'


@app.route('/test')
def test_url_for():
    # please access to http://localhost:5000/test ）：
    print(url_for('hello'))  
   
    print(url_for('user_page', name='tim'))  # output：/user/tim
    print(url_for('user_page', name='peter'))  # output：/user/peter
    
    print(url_for('test_url_for', num=2))  # output：/test?num=2

    return 'Test page'