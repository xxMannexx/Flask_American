# Base de Python
FROM python:3.11-slim

# Evitar interacción en apt
ENV DEBIAN_FRONTEND=noninteractive

# Instalación de dependencias del sistema necesarias para OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx libsm6 libxext6 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python
COPY requirements.txt .

# Instalar Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto expuesto
EXPOSE 8000

# Comando de inicio con Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
