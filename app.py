import datetime
from flask import *
import os
from dotenv import load_dotenv
import database as db
from detectar_cara import detectar_cara
from Face_recognition import reconocer
import decimal
load_dotenv()

app = Flask(__name__,template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("Inicio.html")

@app.route("/home")
def sesion():
    session["id_usuario"] = "4pnNeg"
    cursor = db.database.cursor()
    cursor.execute(f"SELECT numero_tarjeta FROM Tarjeta where usuario_tarjeta = '{session['id_usuario']}'")
    consulta = cursor.fetchone()
    session["numero_tarjeta"] = consulta[0]
    print(consulta, session["numero_tarjeta"])

    return render_template("principal_Iframe.html")
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
    return render_template("reconocimiento_registro.html")

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
    print(carpeta_referencias)
    extensiones_validas = (".jpg", ".jpeg", ".png")

    # Obtener lista de imágenes en la carpeta
    referencias = [
        os.path.join(carpeta_referencias, archivo)
        for archivo in os.listdir(carpeta_referencias)
        if archivo.lower().endswith(extensiones_validas)
    ]

    print(len(referencias))
    print(ruta_completa)
    comprobacion = detectar_cara(ruta_completa)
    print(comprobacion)

    if (comprobacion[0])["is_real"] is False:
        os.remove(ruta_completa)
        return jsonify({'mensaje': 'Estas suplantando una identidad'})
    else:
        if len(referencias) > 2:

            return redirect(url_for('sesion'))
        else:
            return jsonify({'mensaje': 'Falta una'})



@app.route("/inicio_sesion", methods=['POST', 'GET'])
def inicio_sesion():
    return render_template("inicio_sesion.html")

@app.route("/video_inicio_sesion", methods= ["GET","POST"])
def video_inicio_sesion():
    if request.method == "POST":
        id_usuario = (request.form['usuario']).lower()
        session['id_usuario'] = id_usuario
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    imagen = request.files['imagen']
    id_usuario = session['id_usuario']
    carpeta_usuario = os.path.join('imagenes_usuarios', id_usuario)
    os.makedirs(carpeta_usuario, exist_ok=True)

    nombre_archivo = id_usuario + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"
    ruta_completa = os.path.join(carpeta_usuario, nombre_archivo)

    imagen.save(ruta_completa)

    # Carpeta que contiene las imágenes de referencia
    carpeta_referencias = './imagenes_usuarios/' + id_usuario
    print(carpeta_referencias)

    comprobacion = detectar_cara(ruta_completa)
    print(comprobacion)
    if (comprobacion[0])["is_real"] is False:
        os.remove(ruta_completa)
        return jsonify({'mensaje': 'Estas suplantando una identidad'})
    else:
        flag = reconocer(ruta_completa, carpeta_referencias)
        print(flag)
        if flag is True:
            os.remove(ruta_completa)
            return render_template("Inicio.html")
        else:
            return jsonify({'mensaje': 'No se encontraron coincidencias, intente de nuevo'})
    return "esperar"

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))

@app.route("/estado_cuenta_ruta")
def estado_cuenta_ruta():
    lista = []
    cursor = db.database.cursor()
    cursor.execute(f"select saldo from Tarjeta where usuario_tarjeta = '{session['id_usuario']}'")
    consulta = cursor.fetchone()
    numero = consulta[0]
    return render_template('dashboard.html', data= f"${numero}")

@app.route("/transacciones_ruta")
def transacciones_ruta():
    def consultas(columna):
        cursor = db.database.cursor()
        cursor.execute(f"select {columna} from transacciones where tarjeta_transaccion = '{session['numero_tarjeta']}'")
        lista = cursor.fetchall()
        cursor.close()
        return lista
    consulta_id, consulta_tipo, consulta_monto, consulta_fecha, consulta_sql = consultas("id_transaccion"), consultas("tipo_operacion"),consultas("monto_transaccion"),consultas("fecha_transaccion"),[]
    for i in range(0,int(len(consulta_tipo))):
        id = consulta_id[i][0]
        tipo = consulta_tipo[i][0]
        monto = consulta_monto[i][0]
        fecha = consulta_fecha[i][0]
        mierda = {"id":id, "tipo": tipo, "monto":monto, "fecha":fecha}
        consulta_sql.append(mierda)
    return render_template("Transacciones.html", data = consulta_sql)

@app.route("/transferencia_ruta" , methods=["GET","POST"])
def transferencia_ruta():
    return render_template("Transferencias.html")
@app.route("/transferencia_ruta_pago", methods=["GET","POST"])
def transferencia_ruta_pago():
    if request.method == 'POST':
        tarjeta = (request.form['Tarjeta_Destinatario'])
        monto = request.form['Monto']
        concepto = (request.form['concepto']).title()
        cursor = db.database.cursor()
        consulta = "insert into transferencias (emisor_tarjeta, receptor_tarjeta, monto, concepto) values(%s,%s,%s,%s)"
        datos = [(session["numero_tarjeta"]), tarjeta, int(monto), concepto]
        print(datos)
        cursor.execute(consulta,datos)
        db.database.commit()
    return redirect(url_for('transacciones_ruta'))
@app.route("/Pant_pagos")
def pant_pagos():
    return render_template("Pant_pagos.html")

@app.route("/inversiones")
def inversiones():
    return render_template("Inversiones.html")

@app.route("/Prestamos")
def prestamos():
    return render_template()

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.pop('id_usuario',None)
    return redirect(url_for('registro'))

if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 8000))
    # app.run(host="0.0.0.0", port=port)
    app.run(debug=True)

