import datetime

from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("Inicio.html")  # Carga la página con la cámara

@app.route("/iniciar_sesion")
def iniciar_sesion():
    return render_template("Registro.html")

@app.route("/video")
def llamar_video():
    return render_template('reconocimiento.html')

@app.route("/video_recibido", methods=["POST","GET"])
def video_recibido():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontro el archivo'}), 400

    imagen = request.files['imagen']
    usuario_id = 'Osw123'


    carpeta_usuario = os.path.join('imagenes_usuarios',usuario_id)

    #Crea la carpeta si no exite
    os.makedirs(carpeta_usuario, exist_ok=True)

    nombre_archivo = usuario_id + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"
    ruta_completa = os.path.join(carpeta_usuario, nombre_archivo)

    imagen.save(ruta_completa)

    return jsonify({'mensaje': f'Imagen guardada en {ruta_completa}'})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
