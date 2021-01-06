from flask import Flask, flash, redirect, url_for, render_template, request
from datetime import datetime
#from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'clave_secreta_flask'

# Conexion DB

#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'root'
#app.config['MYSQL_DB'] = 'tfm'

#mysql = MySQL(app)

# context processors

@app.context_processor
def date_now():
    return {
        'now': datetime.utcnow()
    }

# Endpoints

@app.route("/")
def main():
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

if __name__ == "__main__":
       app.run(debug=True)   