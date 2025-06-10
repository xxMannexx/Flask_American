from flask import *
import database as db

app = Flask(__name__)

#Rutas de la aplicacion
@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Usuarios")
    usuarios = cursor.fetchall()

    #Convertir los datos a diccionario
    datos = []
    columnas = [col[0] for col in cursor.description]


    for i in usuarios:
        datos.append(dict(zip(columnas, i)))
    cursor.close()

    print(datos)

    return render_template('index.html', data=datos)

@app.route('/usuarios', methods=['GET', 'POST'])
def agregar_usuario():
    username = request.form['username']
    nombre = request.form['nombre']
    contra = request.form['contra']

    if username and nombre and contra:
        cursor = db.database.cursor()
        consulta = 'INSERT INTO Usuarios (username, nombre, contra) VALUES (%s, %s, %s)'
        data = (username, nombre, contra)
        cursor.execute(consulta, data)
        db.database.commit()

    return redirect(url_for('home'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    cursor = db.database.cursor()
    consulta = 'DELETE FROM Usuarios WHERE id = %s'
    data = (id,)
    cursor.execute(consulta, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    username = request.form['username']
    nombre = request.form['nombre']
    contra = request.form['contra']

    if username and nombre and contra:
        cursor = db.database.cursor()
        consulta = 'UPDATE usuarios SET username = %s, nombre = %s, contra = %s WHERE id = %s'
        data = (username, nombre, contra,id)
        cursor.execute(consulta, data)
        db.database.commit()

        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
