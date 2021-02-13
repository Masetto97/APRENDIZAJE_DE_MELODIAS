from flask import Flask, flash, redirect, url_for, render_template, request
from datetime import datetime
import json
import mariadb

app = Flask(__name__)

app.secret_key = 'clave_secreta_flask'

# configuration used to connect to MariaDB
config = {
    'host': '10.168.168.34',
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


# route to return all people
@app.route('/api/people', methods=['GET'])
def index():
   # connection for MariaDB
   conn = mariadb.connect(**config)
   # create a connection cursor
   cur = conn.cursor()
   # execute a SQL statement
   cur.execute("select * from people")

   # serialize results into JSON
   row_headers=[x[0] for x in cur.description]
   rv = cur.fetchall()
   json_data=[]
   for result in rv:
        json_data.append(dict(zip(row_headers,result)))

   # return the results!
   return json.dumps(json_data)



if __name__ == "__main__":
       app.run(debug=True)   