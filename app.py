import datetime
import io
import random
from http.client import HTTPResponse

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import *
import os
from dotenv import load_dotenv
import database as db
from detectar_cara import detectar_cara
from Face_recognition import reconocer, reconocer2
from matplotlib.pyplot import style
from generar_documento import crear_pdf
import decimal
load_dotenv()

style.use('dark_background')

app = Flask(__name__,template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("Inicio.html")



@app.route("/home")
def sesion():
    print(session)
    cursor = db.database.cursor()
    cursor.execute(f"SELECT numero_tarjeta FROM Tarjeta where usuario_tarjeta = '{session['id_usuario']}'")
    consulta = cursor.fetchone()
    cursor.close()
    session["numero_tarjeta"] = consulta[0]
    print(consulta, session["numero_tarjeta"])
    return render_template("principal_Iframe.html", nombre_usuario = session["id_usuario"])


@app.route("/registro", methods=["POST", "GET"])
def registro():
    cursor = db.database.cursor()
    error = "nada"
    if request.method == 'POST':
        correo = (request.form['correo']).lower()
        nombre = (request.form['nombre']).title()
        apellidos = (request.form['apellidos']).title()
        telefono = request.form['telefono']
        fecha = request.form['fecha']


        id_usuario = f"{apellidos[0:2]}{telefono[-2:]}{fecha[-2:]}"
        #em04

        #Consulta para

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
            error = "Alguno de sus datos ya fue registrado, confirme sus datos o contacte con el soporte"
            return render_template("Registro.html", data = error)

    return render_template("Registro.html", data = error)



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
        if len(referencias) == 2:
            print(referencias)
            flag = reconocer2(ruta_completa, carpeta_referencias)
            if flag is True:
                return jsonify({'mensaje': 'Las imagenes estan completas puedes continuar'})
            else:
                os.remove(ruta_completa)
                return jsonify({'mensaje' : 'No son la misma persona'})
        else:
            return jsonify({'mensaje': 'Falta una'})



@app.route("/inicio_sesion", methods=['POST', 'GET'])
def inicio_sesion():

    if session.get('id_usuario') is None:
        data = ''
    else:
        data = {"id_usuario": session['id_usuario']}

    return render_template("inicio_sesion.html", data=data)

@app.route("/video_inicio_sesion", methods= ["GET","POST"])
def video_inicio_sesion():
    if request.method == "POST":
        id_usuario = (request.form['usuario']).lower()
        session['id_usuario'] = id_usuario
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'})

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

    try:
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
                return jsonify({'mensaje' : 'Sesion correcta'})
            else:
                os.remove(ruta_completa)
                return jsonify({'mensaje': 'No se encontraron coincidencias, intente de nuevo'})
    except ValueError:
        os.remove(ruta_completa)
        return jsonify({'mensaje': 'No se detecto un rostro, intente de nuevo'})


@app.route('/Tarjeta')
def tarjeta():
    cursor = db.database.cursor()
    print(session)
    cursor.execute(f"select nombre from Usuarios where id_usuario = '{session['id_usuario']}'")
    nombre_consulta = cursor.fetchone()
    nombre = nombre_consulta[0]
    cursor.close()
    return render_template("Tarjeta.html", nombre = nombre)

@app.route("/tarjeta_recibir", methods=['POST', 'GET'])
def tarjeta_recibir():
    if request.method == 'POST':
        numero_tarjeta = request.form['no_tarjeta']
        usuario_tarjeta = session['id_usuario']
        cvv = request.form['cvv']
        fecha_vencimiento = request.form['expira']
        saldo = random.randint(1000, 100000)
        cursor = db.database.cursor()
        consulta_recibir = "insert into Tarjeta (numero_tarjeta, usuario_tarjeta,nip,cvv, fecha_vencimiento,saldo) values (%s, %s, %s, %s, %s,%s)"

        nip = random.randint(100,10000)

        datos = (numero_tarjeta, usuario_tarjeta,nip,cvv, fecha_vencimiento,saldo)
        cursor.execute(consulta_recibir, datos)
        db.database.commit()
        cursor.close()

    return redirect(url_for('inicio_sesion'))


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))

@app.route("/estado_cuenta_ruta")
def estado_cuenta_ruta():
    print("dashboard:", session)
    lista = []
    cursor = db.database.cursor()
    cursor.execute(f"select saldo from Tarjeta where usuario_tarjeta = '{session['id_usuario']}'")
    consulta = cursor.fetchone()
    numero = consulta[0]
    cursor.close()

    cursor = db.database.cursor()
    cursor.execute(f"select ingresos from estado_cuenta where usuario_cuenta = '{session['numero_tarjeta']}'")
    ingresos_consulta = cursor.fetchone()
    print(ingresos_consulta)
    ingresos = ingresos_consulta[0]
    cursor.close()

    cursor = db.database.cursor()
    cursor.execute(f"select gastos from estado_cuenta where usuario_cuenta = '{session['numero_tarjeta']}'")
    gastos_consulta = cursor.fetchone()
    print(gastos_consulta)
    gastos = gastos_consulta[0]
    cursor.close()


    datos = {
        "saldo": f"${numero}",
        "ingresos": f"${ingresos}",
        "gastos": f"${gastos}",
        "ruta" : session['id_usuario']
    }
    print(datos["ruta"])
    return render_template('dashboard.html', data=datos)

@app.route('/<usuario>/plot.png', methods=["GET"])
def plot_png(usuario):
    fig = create_figure()
    usuario = session['id_usuario']
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    cursor = db.database.cursor()
    cursor.execute(f"select ingresos from estado_cuenta where usuario_cuenta = '{session['numero_tarjeta']}'")
    ingresos_consulta = cursor.fetchone()
    print(ingresos_consulta)
    ingresos = ingresos_consulta[0]
    cursor.close()

    cursor = db.database.cursor()
    cursor.execute(f"select gastos from estado_cuenta where usuario_cuenta = '{session['numero_tarjeta']}'")
    gastos_consulta = cursor.fetchone()
    print(gastos_consulta)
    gastos = gastos_consulta[0]
    cursor.close()

    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    categorias = ['Ingresos', 'Gastos']
    valores = [int(ingresos),(-1)*int(gastos)]

    ax.bar(categorias,valores,color = 'gold')

    ax.set_title('Comparacion Ingresos/Gastos')
    ax.set_xlabel('Tipo de movimiento')
    ax.set_ylabel('Valores')

    return fig
@app.route("/transacciones_ruta")
def transacciones_ruta():
    print("transacciones:", session)
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
    print("transferencia:", session)
    error = "nada"
    return render_template("Transferencias.html", data=error)
@app.route("/transferencia_ruta_pago", methods=["GET","POST"])
def transferencia_ruta_pago():
    if request.method == 'POST':
        tarjeta = (request.form['Tarjeta_Destinatario'])
        monto = request.form['Monto']
        concepto = (request.form['concepto']).title()

        cursor = db.database.cursor()
        cursor.execute(f"select saldo from Tarjeta where numero_tarjeta = '{session['numero_tarjeta']}'")
        saldo = cursor.fetchone()[0]
        cursor.close()

        cursor = db.database.cursor()
        cursor.execute(f"select numero_tarjeta from Tarjeta where numero_tarjeta = '{tarjeta}'")
        comprobacion = cursor.fetchone()
        cursor.close()

        if comprobacion == None:
            error = "No existe la tarjeta a transferir"
            return render_template("Transferencias.html", data= error)
        elif tarjeta == session['numero_tarjeta']:
            error = "no puedes transferirte, autista"
            return render_template("Transferencias.html", data= error)
        elif int(monto) > int(saldo):
            error = "No puedes transferir mas dinero de del que tienes"
            return render_template("Transferencias.html", data= error)
        else:
            cursor = db.database.cursor()
            consulta = "insert into transferencias (emisor_tarjeta, receptor_tarjeta, monto, concepto) values(%s,%s,%s,%s)"
            datos = [(session["numero_tarjeta"]), tarjeta, int(monto), concepto]
            print(datos)
            cursor.execute(consulta,datos)
            db.database.commit()
            return redirect(url_for('transacciones_ruta'))
    return redirect(url_for('transacciones_ruta'))
@app.route("/Pant_pagos", methods=["GET","POST"])
def pant_pagos():
    print("transacciones:", session)
    error = "nada"
    return render_template("Pant_pagos.html", data=error)

@app.route("/Pant_pagos_pago", methods=["GET","POST"])
def pant_pagos_pago():
    if request.method == 'POST':
        servicio = (request.form['servicio'])
        numero = (request.form['numero'])
        monto = request.form['monto']

        cursor = db.database.cursor()
        cursor.execute(f"select saldo from Tarjeta where numero_tarjeta = '{session['numero_tarjeta']}'")
        saldo = cursor.fetchone()[0]
        cursor.close()
        if int(monto) > int(saldo):
            error = "No puedes pagar mas dinero de del que tienes"
            return render_template("Pant_pagos.html", data=error)
        else:
            cursor = db.database.cursor()
            consulta = "insert into pago_servicio (tarjeta_servicio, nombre_servicio, monto_servicio, no_servicio) values(%s,%s,%s,%s)"
            datos = [(session["numero_tarjeta"]), servicio, int(monto), numero]
            print(datos)
            cursor.execute(consulta,datos)
            db.database.commit()
    return redirect(url_for('transacciones_ruta'))
@app.route("/inversiones")
def inversiones():
    print("inversiones:", session)
    lista = {"hay":True, "monto_inversion": 0, "tasa_gat":0, "ganancia_mes": 0, "error":"nada"}
    cursor = db.database.cursor()
    cursor.execute(f"select * from inversion where tarjeta_inversion = '{session['numero_tarjeta']}'")
    consulta = cursor.fetchone()

    if consulta:
        print(consulta)
        lista["monto_inversion"] = consulta[1]
        lista["tasa_gat"] = consulta[2]
        lista["ganancia_mes"] = consulta[3]
    else:
        lista["hay"] = False
    cursor.close()
    return render_template("Inversion.html", data=lista)

@app.route("/inversion_crear", methods=["GET","POST"])
def inversion_crear():
    if request.method == 'POST':
        dinero = (request.form['dinero'])
        cursor = db.database.cursor()
        cursor.execute(f"select saldo from Tarjeta where numero_tarjeta = '{session['numero_tarjeta']}'")
        saldo = cursor.fetchone()[0]
        cursor.close()
        if int(dinero) > int(saldo):
            error = "No puedes invertir mas dinero de del que tienes"
            return render_template("Transferencias.html", data=error)
        else:
            cursor = db.database.cursor()
            data = [session["numero_tarjeta"], int(dinero),0.15,(int(dinero)*0.15)]
            print(data)
            cursor.execute(f"insert into inversion(tarjeta_inversion,monto_inversion,tasa_gat,ganancia_mes) values(%s,%s,%s,%s)", data)
            db.database.commit()
            cursor.close()
    return redirect(url_for('transacciones_ruta'))

@app.route("/Prestamos")
def prestamos():
    print("transacciones:", session)
    lista = {"hay": True, "monto_prestamo": 0, "tasa_prestamo": "activo", "plazo_prestamo": 0}
    cursor = db.database.cursor()
    cursor.execute(f"select * from prestamo where tarjeta_prestamo = '{session['numero_tarjeta']}'")
    consulta = cursor.fetchone()
    if consulta:
        print(consulta)
        lista["monto_prestamo"] = consulta[1]
        lista["tasa_prestamo"] = "activo"
        lista["plazo_prestamo"] = consulta[3]
    else:
        lista["hay"] = False
    cursor.close()
    return render_template("prestamo.html", data = lista)

@app.route("/prestamo_crear", methods=["GET","POST"])
def prestamo_crear():
    if request.method == 'POST':
        dinero = (request.form['dinero'])
        plazos = (request.form['selec'])
        cursor = db.database.cursor()
        data = [session["numero_tarjeta"], int(dinero), 0.25, int(plazos)]
        print(data)
        cursor.execute(
            f"insert into prestamo(tarjeta_prestamo,monto_prestamo,tasa_prestamo,plazo_prestamo) values(%s,%s,%s,%s)", data)
        db.database.commit()
        cursor.close()
        cursor = db.database.cursor()
        cursor.execute(f"select nombre from Usuarios where id_usuario = '{session['id_usuario']}'")
        nombre_consulta = cursor.fetchone()
        nombre = nombre_consulta[0]
        cursor.close()


        id_usuario = session['id_usuario']
        tasa = '25'
        fecha = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        documento = crear_pdf(nombre, session['numero_tarjeta'], id_usuario, fecha, int(dinero), tasa, int(plazos))

        return make_response(documento.read(), 200, {'Content-Type': 'application/pdf',
                                                     'Content-Disposition': f'inline; filename={id_usuario}_reporte.pdf'})
    return redirect(url_for('transacciones_ruta'))

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.pop('id_usuario',None)
    return redirect(url_for('registro'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
    # app.run(debug=True)

