from flask import Flask, flash, redirect, url_for, render_template, request, session,  send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import mariadb
import re
import socket, pickle
import os

# FLASK initial setup
app = Flask(__name__)
app.secret_key = 'clave_secreta_flask'

# Folder to upload the files before saving them in the database
UPLOAD_FOLDER = 'Upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensions allowed for uploading files
ALLOWED_EXTENSIONS = {
    'mid', 
    'midi', 
    'xml'
}

# Global variables
CURRENT_USER_ID = 0
TITLE_FILE_PROCESSED = ''
FLAG_UPLOAD_FILE = 1

# Configuration used to connect to MariaDB
config = {
    'host': 'mariadb',
    'port': 3306,
    'user': 'user',
    'password': 'password',
    'database': 'TFM'
}

#########################################
########### Utility functions ###########
#########################################

# Function to convert binary data to proper format and save it to hard drive
def write_file(data, filename):
    with open(os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], filename)),  'wb') as file:
        file.write(data)

# Function to check that the uploaded file has the allowed Extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to convert a data file to binary format
def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

# Function to get the System date
@app.context_processor
def date_now():
    return {
        'now': datetime.utcnow()
    }

#########################################
############### ENDPOINTS ###############
#########################################

# Endpoint where the login is made to the system
@app.route('/', methods=['GET', 'POST'])
def login():

    # Output message if something goes wrong...
    msg = ''

    # Declaration of the global variable Current User Id to be able to modify its value
    global CURRENT_USER_ID

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

        # If account exists in User table in out database
        if account:
            # Get the User Id from the BBDD
            CURRENT_USER_ID = account[0]
            #Let's go to the home page
            return redirect(url_for('index'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect Login'

    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


# Endpoint where to create a new user in the system
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

        # Check if account exists using MariaDB
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USUARIO WHERE Usuario = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error and validation checks
        if account:
            msg = 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'The username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please complete all the fields in the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USUARIO VALUES (NULL, %s, %s, %s, %s)', (name, username, password, email))
            conn.commit()
            msg = 'Registration completed!'
    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please complete all the fields in the form!'

    # Show registration form with message (if any)
    return render_template('registro.html', msg=msg)


# Endpoint where the main information of the application is displayed
@app.route("/index")
def index():
    return render_template('index.html')


# Endpoint where the files processed by the user are displayed
@app.route("/biblioteca", methods=['GET', 'POST'])
def biblioteca():

    # Output message if something goes wrong...
    # msg = os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], 'prueba.mid'))

    # connection for MariaDB
    conn = mariadb.connect(**config)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM CANCION WHERE Usuario = %s ' % CURRENT_USER_ID)

    songs = cursor.fetchall()

    if request.method == 'POST':

        
        Selected_Song = request.form['submit_button']

        processed = False

        if Selected_Song[0:1] == 'p':

            processed = True

            Selected_Song = Selected_Song[1:]


        cursor.execute('SELECT Fichero FROM FICHERO WHERE Cancion = %s' % Selected_Song)

        Song_Files = cursor.fetchone()

        if processed:

          Song_Files = cursor.fetchone()          

        cursor.execute('SELECT Titulo FROM CANCION WHERE ID = %s AND Usuario = %s ', (Selected_Song, CURRENT_USER_ID))

        aux = cursor.fetchone()

        Final_Title = aux[0] + '.mid'

        if processed:
            
            Final_Title = aux[0] + '_procesado.mid'
            
        write_file(Song_Files[0], os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], Final_Title)) )

        #return render_template('biblioteca.html',songs=songs)

        uploads = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])

        return send_from_directory(directory=uploads, filename=Final_Title)


    return render_template('biblioteca.html',songs=songs) 


# Endpoint where the file to be processed is uploaded and sent
@app.route("/subir", methods=['GET', 'POST'])
def subir():

    # Output message if something goes wrong...
    msg = ''

    # Declaration of the global variables Flag Upload File and Title File Process to be able to modify its values
    global FLAG_UPLOAD_FILE
    global TITLE_FILE_PROCESSED

    # If there isn´t file being processed
    if FLAG_UPLOAD_FILE == 1:
        
        # connection for MariaDB
        conn = mariadb.connect(**config)
        cursor = conn.cursor()

        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST':

            # check if the post request has the file part
            if 'file' not in request.files and 'Titulo' not in request.form and 'estilo' not in request.form:
                msg = 'Please complete all the fields in the form!'

                return redirect(request.url)

            # Create variables for easy access
            file       = request.files['file']
            File_title = request.form['Titulo']

            # Assign the title to the global variable
            TITLE_FILE_PROCESSED = File_title

            # Check if file exists using MariaDB
            cursor.execute('SELECT * FROM CANCION WHERE Usuario = %s AND Titulo = %s', (CURRENT_USER_ID,File_title))
            Check_existence = cursor.fetchone()

            # If the song already exists
            if Check_existence:
                msg = 'The file already exists!'

            # If the song doesn't exist
            else:

                # if the path is wrong
                if file.filename == '':
                    msg ='Please complete all the fields in the form!'
                    return redirect(request.url)

                # If the file has a correct format
                if file and allowed_file(file.filename):

                    # The file is saved in the Upload folder
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], filename)))    

                    # The file data is saved in the BBDD
                    cursor.execute('INSERT INTO CANCION VALUES (NULL, %s, %s, %s, %s)', (File_title, 0 , "CLASICO", CURRENT_USER_ID))   
                    conn.commit()

                    # The ID with which the song was saved is obtained
                    cursor.execute('SELECT * FROM CANCION WHERE Usuario = %s AND Titulo = %s', (CURRENT_USER_ID, File_title))
                    Song_ID = cursor.fetchone()

                    # If the song was added correctly
                    if Song_ID:

                        # The file is converted to binary
                        file = convertToBinaryData(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        # The file is added to the BBDD
                        cursor.execute('INSERT INTO FICHERO VALUES (NULL, %s, %s)', (file, Song_ID[0]))   
                        conn.commit()
 
                        # The file is sent through a Socket
                        s = socket.socket()
                        s.connect(('ia', 5000)) #Socket Configuration

                        # The title is sent
                        s.send(File_title.encode())

                        # The file is opened and sent
                        filetosend = open(os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], filename)), "rb")
                        aux = filetosend.read(1024)

                        while aux:
                            s.send(aux)
                            aux = filetosend.read(1024)

                        filetosend.close()

                        # Final flag is sent
                        s.send('fin'.encode())

                        # The connection is closed
                        print(s.recv(1024))
                        s.shutdown(2)
                        s.close()

                        msg = 'Song uploaded and sent to process!!'

                        # The flag is updated to not allow a new song to be processed
                        FLAG_UPLOAD_FILE = 0

        return render_template('subir.html', msg=msg)

    # If there is file being processed
    else:
        # A flash message is sent to the user
        flash('EXISTE UN ARCHIVO PROCESANDO, ESPERE A QUE TERMINE ESTA OPERACIÓN')
        return render_template('index.html')


# Endpoint where the processed song is received and saved in the BBDD
@app.route("/procesado", methods=['GET', 'POST'])
def procesado():

    # Declaration of the global variables Flag Upload File to be able to modify its value
    global FLAG_UPLOAD_FILE

    #The file is obtained through the Request
    processed_file = request.files['file1']

    # connection for MariaDB
    conn = mariadb.connect(**config)
    cursor = conn.cursor()

    # The id of the song sent to be processed is obtained
    cursor.execute('SELECT * FROM CANCION WHERE Usuario = %s AND Titulo = %s', (CURRENT_USER_ID, TITLE_FILE_PROCESSED))
    Song_ID = cursor.fetchone()

    # If the song has ID
    if Song_ID:

        # It indicates that the song has been processed
        cursor.execute('UPDATE CANCION SET Procesado=1 where Usuario = %s AND Titulo = %s', (CURRENT_USER_ID, TITLE_FILE_PROCESSED))
        conn.commit()

        # The file obtained is saved in the Upload folder
        filename = secure_filename(processed_file.filename)
        processed_file.save(os.path.join(os.getcwd(),os.path.join(app.config['UPLOAD_FOLDER'], filename)))

        # The file is converted to binary
        file = convertToBinaryData(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # The file is added to the BBDD
        cursor.execute('INSERT INTO FICHERO VALUES (NULL, %s, %s)', (file, Song_ID[0]))    
        conn.commit()
  
    # The flag is updated so that a new process is allowed
    FLAG_UPLOAD_FILE = 1

    # A flash message is sent to the user
    flash('EL ARCHIVO YA HA SIDO PROCESADO, YA PUEDE CARGAR OTRO')

    return ''

# Endpoint where the session is closed
@app.route('/logout')
def logout():
   return redirect('/') 

#APP MAIN
if __name__ == "__main__":
       app.run(debug=True, host='0.0.0.0')