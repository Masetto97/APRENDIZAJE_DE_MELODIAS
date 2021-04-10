from flask import Flask, flash, redirect, url_for, render_template, request, session
from datetime import datetime
import json
import mariadb
import re
import socket

app = Flask(__name__)

app.secret_key = 'clave_secreta_flask'

# configuration used to connect to MariaDB
config = {
    'host': 'mariadb',
    'port': 3306,
    'user': 'user',
    'password': 'password',
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
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Login incorrecto'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

         # Check if account exists using MySQL
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USUARIO WHERE Usuario = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USUARIO VALUES (NULL, %s, %s, %s, %s)', (name, username, password, email,))
            conn.commit()
            msg = 'You have successfully registered!'
    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registro.html', msg=msg)

@app.route("/subir")
def subir():
    return render_template('subir.html') 

@app.route("/index")
def index():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 5000 # Puerto de comunicacion
        # Realizamos la conexion al la IP y puerto
        sock.connect(('ia',port))
        # Create an instance of ProcessData() to send to server.
        variable = 'HOLA SOY EDU'
        # Pickle the object and send it to the server
        data_string = pickle.dumps(variable)
        s.send(data_string)
        # Cerramos el socket
        sock.close()
        # Mostramos los datos recibidos
        print(data.decode())

        return render_template('index.html', data=data)

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
   return redirect('/')

if __name__ == "__main__":
       app.run(debug=True, host='0.0.0.0')   
