from flask import Flask, flash, redirect, url_for, render_template, request, session
from datetime import datetime
import json
import mariadb

app = Flask(__name__)

app.secret_key = 'clave_secreta_flask'

# configuration used to connect to MariaDB
config = {
    'host': '172.17.0.2',
    'port': 3306,
    'user': 'root',
    'password': 'Password123!',
    'database': 'TFM'
} 


@app.context_processor
def date_now():
    return {
        'now': datetime.utcnow()
    }

# Endpoints

@app.route('/', methods=['GET', 'POST'])
def login():
     # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        # connection for MariaDB
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USUARIO WHERE Usuario = %s AND Password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Login incorrecto'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route("/index")
def index():
      return render_template('index.html')

@app.route("/ajustes")
def ajustes():
                return render_template('ajustes.html') 

@app.route("/biblioteca")
def biblioteca():
                return render_template('biblioteca.html') 

@app.route("/cargar")
def cargar():
                return render_template('cargar.html') 

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('/'))

if __name__ == "__main__":
       app.run(debug=True)   
