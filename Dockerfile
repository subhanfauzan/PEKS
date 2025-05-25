# Gunakan base image ringan Python
FROM python:3.10-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Salin semua file ke dalam container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pastikan folder uploads ada
RUN mkdir -p uploads

# Jalankan aplikasi
CMD ["python", "app.py"]
