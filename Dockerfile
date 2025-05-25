# Gunakan image Python
FROM python:3.10-slim

# Atur direktori kerja
WORKDIR /app

# Salin semua file ke image
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Buat folder uploads jika belum ada
RUN mkdir -p uploads

# Jalankan aplikasi
CMD ["python", "app.py"]
