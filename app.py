from flask import Flask, request, send_file, render_template_string
import os, json
from crypto_utils import *

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
METADATA_FILE = "data.json"

# Load or generate key pair
if not os.path.exists("private.pem"):
    priv_key, pub_key = generate_keys()
    save_keys(priv_key, pub_key)
else:
    priv_key, pub_key = load_keys()

# Load metadata
if os.path.exists(METADATA_FILE):
    try:
        with open(METADATA_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}
else:
    data = {}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PEKS SIAKAD Nilai</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      textarea { font-family: monospace; }
    </style>
  </head>
  <body class="bg-light">
    <div class="container py-5">
      <h2 class="mb-4">Sistem Nilai dengan PEKS</h2>
      {% if message %}
        <div class="alert alert-{{ 'success' if status == 'success' else 'danger' }}">{{ message }}</div>
      {% endif %}
      <div class="row">
        <div class="col-md-6">
          <h5>Upload PDF Nilai (Dosen)</h5>
          <form method="POST" enctype="multipart/form-data">
            <div class="mb-3">
              <label class="form-label">Pilih File PDF:</label>
              <input type="file" class="form-control" name="pdf" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Kata Kunci:</label>
              <input type="text" class="form-control" name="upload_keyword" required>
            </div>
            <button type="submit" class="btn btn-primary">Upload & Enkripsi</button>
          </form>
        </div>
        <div class="col-md-6">
          <h5>Cari PDF Nilai (Mahasiswa)</h5>
          <form method="POST">
            <div class="mb-3">
              <label class="form-label">Masukkan Kata Kunci:</label>
              <input type="text" class="form-control" name="search_keyword" required>
            </div>
            <button type="submit" class="btn btn-success">Cari</button>
          </form>
        </div>
      </div>

      <hr>
      <h5>Daftar Dokumen Terenkripsi</h5>
      <ul class="list-group mb-4">
        {% for filename in file_list %}
          <li class="list-group-item">{{ filename }}</li>
        {% else %}
          <li class="list-group-item">Belum ada dokumen terenkripsi.</li>
        {% endfor %}
      </ul>

      {% if encrypted_index %}
      <h5>Hasil Enkripsi Kata Kunci (Index PEKS)</h5>
      <textarea class="form-control mb-3" rows="3" readonly>{{ encrypted_index }}</textarea>
      {% endif %}

      {% if trapdoor_hash %}
      <h5>Hasil Hash Kata Kunci (Trapdoor)</h5>
      <textarea class="form-control" rows="3" readonly>{{ trapdoor_hash }}</textarea>
      {% endif %}
    </div>
  </body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    status = ""
    encrypted_index = ""
    trapdoor_hash = ""

    if request.method == "POST":
        if "pdf" in request.files and "upload_keyword" in request.form:
            # Upload PDF
            file = request.files["pdf"]
            keyword = request.form["upload_keyword"]
            filename = file.filename
            index = generate_index(keyword, pub_key)
            index_b64 = index.hex()
            encrypted_index = index_b64
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            data[index_b64] = filename
            with open(METADATA_FILE, "w") as f:
                json.dump(data, f)
            message = "File berhasil diunggah dan dienkripsi."
            status = "success"

        elif "search_keyword" in request.form:
            # Pencarian PDF
            keyword = request.form["search_keyword"]
            trapdoor = generate_trapdoor(keyword)
            trapdoor_hash = trapdoor.hex()
            for index_hex, filename in data.items():
                index = bytes.fromhex(index_hex)
                if match(index, trapdoor, priv_key):
                    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
            message = "Kata kunci salah atau PDF tidak ditemukan."
            status = "error"

    file_list = list(set(data.values()))
    return render_template_string(HTML_TEMPLATE, message=message, status=status, file_list=file_list, encrypted_index=encrypted_index, trapdoor_hash=trapdoor_hash)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)