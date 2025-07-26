# Usa una immagine leggera con Python
FROM python:3.12

# Imposta la working directory
WORKDIR /app

# Copia i file del progetto
COPY . .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Avvia il producer
CMD ["python", "consumer.py"]
