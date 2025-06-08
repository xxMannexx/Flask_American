import os

try:
    os.remove('prueba de mierda.py')
except OSError as e:
    print(f'No se pudo eliminar por que: {e}')