from deepface import DeepFace

def detectar_cara(ruta):
    detector = DeepFace.extract_faces(img_path=ruta,anti_spoofing=True)
    return detector
