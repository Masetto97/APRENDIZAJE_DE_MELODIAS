from flask import Flask, flash, redirect, url_for, render_template, request, session
from datetime import datetime
import json
import mariadb
import re
import socket, pickle

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

ID_USUARIO_ACTUAL = 1

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
        cursor.execute('SELECT * FROM USUARIO WHERE Usuario = %s AND Password = %s', (username, password))
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
            msg = 'El usuario ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Direcion de correo invalida!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario debe contener solo caracteres y números!'
        elif not username or not password or not email:
            msg = 'Por favor rellena el formulario!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USUARIO VALUES (NULL, %s, %s, %s, %s)', (name, username, password, email))
            conn.commit()
            msg = 'You have successfully registered!'
    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Por favor rellena el formulario!'
    # Show registration form with message (if any)
    return render_template('registro.html', msg=msg)


@app.route("/subir", methods=['GET', 'POST'])
def subir():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'titulo' in request.form and 'estilo' in request.form and 'ruta' in request.form:
        # Create variables for easy access
        titulo = request.form['titulo']
        estilo = request.form['estilo']
        ruta = request.form['ruta']

         # Check if account exists using MySQL
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM CANCION WHERE Titulo = %s', (titulo,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'La cancion ya fue registrada!'
        elif not re.match(r'[A-Za-z0-9]+', titulo):
            msg = 'El titulo solo debe contener letras y numeros!'
        elif not titulo or not ruta:
            msg = 'Por favor rellena el formulario!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO CANCION VALUES (NULL, %s, %s, %s, %s, %s)', (titulo, datetime.now(), 'N', estilo, ID_USUARIO_ACTUAL))
            conn.commit()
            cursor.execute('INSERT INTO FICHERO VALUES (NULL, %s, %s)', (titulo, ruta, ID_USUARIO_ACTUAL))
            conn.commit()
            msg = 'Registro Exitoso!'
    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Por favor rellena el formulario!'

    # Show registration form with message (if any)
    return render_template('subir.html', msg=msg) 



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
   return redirect('/')

if __name__ == "__main__":
       app.run(debug=True, host='0.0.0.0')   
