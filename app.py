from flask import Flask, request, jsonify, render_template
import cv2
from deepface import DeepFace as pito
import face_recognition
import numpy as np
import base64

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("Inicio.html")  # Carga la página con la cámara

@app.route("/video")
def llamar_video():
    return render_template('reconocimiento.html')

@app.route("/video_recibido", methods=["POST","GET"])
def video_recibido():
    url = request.json["image"]
    base = base64.b64decode(url.split(",")[1])
    matriz = np.frombuffer(base, np.uint8)
    frame = cv2.imdecode(matriz, cv2.IMREAD_COLOR)

    detectar_cara = face_recognition.face_locations(frame)

    if detectar_cara:
        return jsonify({"message": "Hay rostro detectado"})
    else:
        return jsonify({"message": "No se detectó una cara."})


if __name__ == "__main__":
    app.run(debug=True)
