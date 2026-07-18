# Usa una imagen oficial de Python ligera
FROM python:3.14-slim

# Evita que Python escriba archivos .pyc y fuerza salida de consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema requeridas (opcional pero recomendado)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de dependencias
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Comando por defecto (aunque será sobrescrito por docker-compose)
CMD ["python", "main.py"]
