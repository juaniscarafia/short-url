from configparser import Error, MissingSectionHeaderError
from flask import Flask, render_template, url_for, flash, request, redirect, jsonify
from flask_mysql_connector import MySQL
import sqlite3
import shortuuid

# Inicializo APP
app = Flask(__name__)

# Endpoint
endpoint = 'http://short.url'

# Conexion MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE'] = 'db_enlaces_cortos'

# Llave secreta para usar mensajes flash
app.secret_key="C1v3S3cr3T"

# Inicializo la Base de Datos
mysql = MySQL(app)

# Ruta Inicial
@app.route('/', methods=['GET'])
def inicio():
    try:
        return render_template('index.html'), 200
    except:
        return render_template('404.html'), 404

# Ruta para crear enlace corto y almacenar en la base de datos
@app.route('/crear_enlace_corto', methods=['POST'])
def crear_enlace_corto():
    try:
        if request.method == 'POST':
            # Capturo la URL
            url = request.form['url']
            cursor = mysql.connection.cursor()

            # ciclo para validar enlace corto que no se duplique
            while True:
                # Genero el enlace corto
                enlace_corto = shortuuid.ShortUUID().random(length=7)

                # Consulto a la BD si existe el enlace corto
                cursor.execute("SELECT * FROM ENLACES WHERE ENLACE_CORTO = BINARY %s", (enlace_corto,))

                if not cursor.fetchone():
                    break
            
            # Consulto si en la BD existe la URL
            cursor.execute("SELECT ENLACE_CORTO FROM ENLACES WHERE URL = BINARY %s", (url,))
            data = cursor.fetchone()
            
            if data:
                flash(endpoint + '/' + data[0])
                return redirect(url_for('inicio')), 302

            #Ingreso en la BD la url enviada
            cursor.execute(
                "INSERT INTO enlaces (url, enlace_corto) VALUES (%s,%s)", (url, enlace_corto)
            )
            
            # Guardo cambios en la BD
            mysql.connection.commit()

            # Cierro la conexión
            cursor.close()
            nuevo_enlace = endpoint + '/' + enlace_corto
            flash(nuevo_enlace)
            return redirect(url_for('inicio')), 302
    except:
        return render_template('404.html'), 404

# Ruta para ir a URL de Base de datos
@app.route('/<id>')
def obtener_url(id):
    try:
        cursor = mysql.connection.cursor()

        #Busco en la BD la dirección URL
        cursor.execute("SELECT URL FROM ENLACES WHERE ENLACE_CORTO = BINARY %s",(id,))

        # Guardo en variable el resultado
        data = cursor.fetchone()

        # Cierro conexión a BD
        cursor.close()

        return render_template('ads.html',url=data[0]), 200
    except:
        return render_template('404.html'), 404

#Inicio APP
if __name__ == "__main__":
    app.run(port=80, debug=True)