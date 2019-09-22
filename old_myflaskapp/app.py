from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Dosare
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, DateField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from zeep import Client
import datetime

app = Flask(__name__)

# config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'myflaskapp'
app.config['MYSQL_PASSWORD'] = 'doaralmeu'
app.config['MYSQL_DB'] = 'edosare'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)

Dosare = Dosare()

#register form class
class RegisterForm(Form):
    name = StringField('Name', validators=[validators.Length(min=1, max=50)])
    username  = StringField('Username', validators=[validators.Length(min=4, max=25)])
    email  = StringField('eMail', validators=[validators.Length(min=6, max=50)])
    password  = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#search form class
class SearchForm(Form):
    numarDosar = StringField('Numar Dosar: &nbsp', validators=[validators.Length(min=0, max=40)])
    obiectDosar  = StringField('Obiect Dosar: &nbsp', validators=[validators.Length(min=0, max=40)])
    numeParte  = StringField('Nume Parte: &nbsp', validators=[validators.Length(min=0, max=40)])
    institutie  = StringField('Institutie: &nbsp', validators=[validators.Length(min=0, max=40)])
    dataInregistratiiStart = DateField('Data Inregistrarii Start: &nbsp', format='%d/%m/%y', validators=[(validators.Optional())])
    dataInregistratiiStop = DateField('Data Inregistrarii Stop: &nbsp', format='%d/%m/%y', validators=[(validators.Optional())])
    dataUltimeiModificariStart = DateField('Data Ultimei Modificari Start: &nbsp', format='%d/%m/%y', validators=[(validators.Optional())])
    dataUltimeiModificariStop = DateField('Data Ultimei Modificari Stop: &nbsp', format='%d/%m/%y', validators=[(validators.Optional())])


#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login first', 'danger')
            return redirect(url_for('login'))
    return wrap

#index
@app.route('/')
def index():
    return render_template('home.html')

#about
@app.route('/about')    
def about():
    return render_template('about.html')

@app.route('/dosar/<string:id>/')    
def dosar(id):
    return render_template('dosar.html', id=id)

#user register
@app.route('/register', methods=['GET', 'POST'])    
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor 
        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)        

#search
@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    searchForm = SearchForm(request.form)
    searchResult = ""
    if request.method == 'POST' and searchForm.validate():
        numarDosar = searchForm.numarDosar.data
        obiectDosar  = searchForm.obiectDosar.data
        numeParte  = searchForm.numeParte.data
        institutie  = searchForm.institutie.data
        dataInregistratiiStart = datetime.datetime(2016,5,1)
        dataInregistratiiStop = datetime.datetime(2016,6,1)
        dataUltimeiModificariStart = searchForm.dataUltimeiModificariStart.data
        dataUltimeiModificariStop = searchForm.dataUltimeiModificariStop.data

        client = Client(wsdl='http://portalquery.just.ro/query.asmx?WSDL')
        
        searchResult = client.service.CautareDosare(numarDosar, obiectDosar, numeParte, institutie, dataInregistratiiStart, dataInregistratiiStop)

    return render_template('search.html', form=searchForm, result=searchResult)    

#user login
@app.route('/login', methods =['GET','POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create cursor
        cur = mysql.connection.cursor()

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result>0:
            #get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed identification
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error)
            #close connection
            cur.close()


        else: 
            error = 'Username not found'
            return render_template('login.html', error=error)              

    return render_template('login.html')


#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


#single dosar
@app.route('/dosare')    
@is_logged_in
def dosare():
    return render_template('dosare.html', dosare = Dosare)

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)