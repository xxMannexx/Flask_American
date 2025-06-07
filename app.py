import datetime
from flask import *
import os
from dotenv import load_dotenv
import database as db
from detectar_cara import detectar_cara

load_dotenv()

app = Flask(__name__,template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("Inicio.html")

@app.route("/registro", methods=["POST", "GET"])
def registro():
    cursor = db.database.cursor()
    if request.method == 'POST':
        correo = (request.form['correo']).lower()
        nombre = (request.form['nombre']).lower()
        apellidos = (request.form['apellidos']).lower()
        telefono = request.form['telefono']
        fecha = request.form['fecha']


        id_usuario = f"{apellidos[0:2]}{telefono[-2:]}{fecha[-2:]}"
        #em04
        Flag_Comprobation = False

        if nombre.isdigit() is True or apellidos.isdigit() is True:
            Flag_Comprobation = True
            print(Flag_Comprobation)
        for llave, valor in {"correo": correo, "nombre": f"{str(nombre)} {str(apellidos)}","telefono": telefono}.items():
            cursor.execute(f"SELECT * FROM Usuarios WHERE {llave} = %s",[valor])
            resultado = cursor.fetchall()
            print(resultado)
            if str(resultado) == "[]":
                break
            else:
                Flag_Comprobation = True
        print(Flag_Comprobation)
        if Flag_Comprobation is False:
            consulta = 'INSERT INTO Usuarios (id_usuario,nombre,correo,telefono,fecha_nacimiento) VALUES (%s,%s,%s,%s,%s)'
            data = [id_usuario,f"{str(nombre)} {str(apellidos)}",correo,telefono,fecha]
            cursor.execute(consulta, data)
            db.database.commit()
            session['id_usuario'] = id_usuario
            print(session['id_usuario'])
            return redirect(url_for('llamar_video'))

        else:
            return redirect(url_for('index'))
    return render_template("Registro.html")

@app.route("/video")
def llamar_video():
    return render_template("reconocimiento.html")

@app.route("/video_recibido", methods=["POST", "GET"])
def video_recibido():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    imagen = request.files['imagen']


    carpeta_usuario = os.path.join('imagenes_usuarios', session['id_usuario'])
    os.makedirs(carpeta_usuario, exist_ok=True)

    nombre_archivo = session['id_usuario'] + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"
    ruta_completa = os.path.join(carpeta_usuario, nombre_archivo)

    imagen.save(ruta_completa)

    # Carpeta que contiene las imágenes de referencia
    carpeta_referencias = './imagenes_usuarios/' + session['id_usuario']

    extensiones_validas = (".jpg", ".jpeg", ".png")

    # Obtener lista de imágenes en la carpeta
    referencias = [
        os.path.join(carpeta_referencias, archivo)
        for archivo in os.listdir(carpeta_referencias)
        if archivo.lower().endswith(extensiones_validas)
    ]

    print(len(referencias))

    comprobacion = detectar_cara(ruta_completa)
    print(comprobacion)
    if (comprobacion[0])["is_real"] is False:
        print('Estas suplantando a una persona')
    else:
        if len(referencias) > 2:
            return redirect(url_for('sesion'))
    return jsonify({'mensaje': 'Imagenes completas'})


@app.route("/home")
def sesion():
    return render_template("principal_Iframe.html")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.pop('id_usuario',None)
    return redirect(url_for('registro'))

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))

if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 8000))
    # app.run(host="0.0.0.0", port=port)
    app.run(debug=True)

