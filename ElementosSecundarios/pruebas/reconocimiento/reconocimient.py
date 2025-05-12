from deepface import DeepFace

# # try:
# #     try:
# #         raise ValueError("Primer error")
# #     except ValueError as e:
# #         raise RuntimeError("Segundo error") from e
# # except Exception as e:
# #     print("Segundo error:", e)
# #     print("Primer error (causa):", e.__cause__)
# from deepface import DeepFace
#
#
#
#
# try:
#     result = DeepFace.verify(
#         img1_path="./fotos/foto.png",
#         img2_path="./fotos/ric.png",
#         model_name="Facenet",
#         detector_backend="retinaface",
#         anti_spoofing=True
#     )
#
#     print(result)
#     print(result["verified"])
# except Exception as e:
#     print(e)
#     causa = e.__cause__
#     print(causa)
#     if str(causa) == 'Spoof detected in given image.':
#         print('Se detecto un intento de suplantacion de imagen.')
#
face = DeepFace.extract_faces(
    img_path = 'fotos/Img2.png',
    anti_spoofing = True
)

print(face)

# import os
# from deepface import DeepFace
#
# # Imagen a validar
# img_actual = "img1.jpg"
#
# # Carpeta que contiene las imágenes de referencia
# carpeta_referencias = "./fotos"
#
# extensiones_validas = (".jpg", ".jpeg", ".png")
#
# # Obtener lista de imágenes en la carpeta
# referencias = [
#     os.path.join(carpeta_referencias, archivo)
#     for archivo in os.listdir(carpeta_referencias)
#     if archivo.lower().endswith(extensiones_validas)
# ]
#
# print(referencias)
#
# coincidencias = 0
# for ref in referencias:
#     try:
#         resultado = DeepFace.verify(
#             img_actual,
#             ref,
#             model_name="Facenet",
#             detector_backend="retinaface",
#             enforce_detection=False
#         )
#         if resultado["verified"]:
#             coincidencias += 1
#     except Exception as e:
#         print(f"Error al verificar con {ref}: {e}")
# print(coincidencias)
#
# if coincidencias >= 2:
#     print(f"Bienvenido {referencias[0].split('\\')[1]} ")
# else:
#     print("Verificación fallida.")


r = DeepFace.extract_faces(img_path='fotos/foto.png', anti_spoofing=True)

print(r)


