import os
from deepface import DeepFace

def reconocer(imagen_usuario,ruta):
    img_actual = imagen_usuario

    # Carpeta que contiene las imágenes de referencia
    carpeta_referencias = ruta

    extensiones_validas = (".jpg", ".jpeg", ".png")

    # Obtener lista de imágenes en la carpeta
    referencias = [
        os.path.join(carpeta_referencias, archivo)
        for archivo in os.listdir(carpeta_referencias)
        if archivo.lower().endswith(extensiones_validas)
    ]

    print(referencias)

    coincidencias = 0
    for ref in referencias:
        try:
            resultado = DeepFace.verify(
                img_actual,
                ref,
                model_name="Facenet",
                detector_backend="retinaface",
                enforce_detection=False
            )
            if resultado["verified"]:
                coincidencias += 1
        except Exception as e:
            print(f"Error al verificar con {ref}: {e}")
    print(coincidencias)

    if coincidencias >= 2:
        return True
    else:
        return False



