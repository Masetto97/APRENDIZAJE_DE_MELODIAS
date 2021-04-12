from flask import Flask, flash, redirect, url_for, render_template, request, session,  send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import mariadb
import re
import socket, pickle
import os

app = Flask(__name__)

app.secret_key = 'clave_secreta_flask'

#Carpeta para subir los archivo antes de guardarlos en la BBDD o procesarlos
UPLOAD_FOLDER = 'Upload' # /ruta/a/la/carpeta
ALLOWED_EXTENSIONS = set(['txt', 'mid', 'png', 'jpg', 'midi', 'xml'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Usuario Actual
ID_USUARIO_ACTUAL = 0

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
        cursor.execute('SELECT * FROM USUARIO WHERE Usuario = %s AND Password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            
            ID_USUARIO_ACTUAL = account[0]
            print('EL USUARIO ACTUAL ES: ')
            print (ID_USUARIO_ACTUAL)
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


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/biblioteca")
def biblioteca():
    s = socket.socket()
    s.connect(('ia', 5000))
    filetosend = open("./entrada.mp3", "r")
    aux = filetosend.read(1024)
    while aux:
        print("Sending...")
        s.send(aux)
        aux = filetosend.read(1024)
    filetosend.close()
    s.send('fin')
    print("Done Sending.")
    print(s.recv(1024))
    s.close()

    return render_template('biblioteca.html') 


@app.route("/subir", methods=['GET', 'POST'])
def subir():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'ruta' in request.form:# and 'titulo' in request.form and 'ruta' in request.form:
        # Create variables for easy access
        #titulo = request.form['titulo']
        ruta = request.files['ruta']
 

        filename = secure_filename(ruta.filename)
        print (os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"]))
        send_from_directory(os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"]),filename,as_attachment=True,)
        #ruta.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        msg = 'Registro Exitoso!'
    # Show registration form with message (if any)
    return render_template('subir.html', msg=msg) 



@app.route('/logout')
def logout():
   return redirect('/') 

if __name__ == "__main__":
       app.run(debug=True, host='0.0.0.0')   
