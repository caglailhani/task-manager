# backend/Dockerfile (sade)
FROM python:3.10

WORKDIR /app

# Bağımlılıklar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
