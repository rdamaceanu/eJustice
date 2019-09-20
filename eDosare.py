from flask import Flask, render_template
from flask_mysqldb import MySQL

eDosare = Flask(__name__)

# config MySQL
eDosare.config['MYSQL_HOST'] = 'localhost'
eDosare.config['MYSQL_USER'] = 'myflaskapp'
eDosare.config['MYSQL_PASSWORD'] = 'doaralmeu'
eDosare.config['MYSQL_DB'] = 'edosare'
eDosare.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(eDosare)

# comentariu
# comentariu 2

# index
@eDosare.route('/')
def index():
    return render_template('index.html')

# about
@eDosare.route('/about')
def about():
    return render_template('about.html')    

# register
@eDosare.route('/register')
def register():
    return render_template('register.html')   


@eDosare.route('/login')
def login():
    return render_template('login.html')   

if __name__ == '__main__':
    eDosare.run(debug=True)