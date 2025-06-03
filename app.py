from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import os
import uuid

app = Flask(__name__)
# Pastikan Flask tahu di mana mencari template HTML.
# Secara default, Flask mencari folder bernama 'templates' di direktori yang sama dengan app.py.
# Pastikan index.html (dan editor.html jika ada) ada di dalam folder 'templates'.

# Pastikan folder 'static' ada di direktori yang sama dengan app.py,
# dan styles.css ada di dalam folder 'static'.
# Flask akan secara otomatis menyajikan file dari folder 'static' melalui URL '/static'.

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
# STATIC_FOLDER = 'static' # Flask menangani ini secara default

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
# os.makedirs(STATIC_FOLDER, exist_ok=True) # Pastikan Anda membuat folder ini secara manual

@app.route('/')
def index():
    return render_template('index.html') # Akan mencari 'templates/index.html'

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    # Disarankan untuk melakukan validasi file (misalnya, tipe file, ukuran) di sini
    if file: # Pastikan file ada
        # Membuat nama file unik untuk menghindari konflik
        ext = os.path.splitext(file.filename)[1] # Dapatkan ekstensi file asli
        if not ext: # Jika tidak ada ekstensi, default ke .png
            ext = '.png'
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        # Setelah file disimpan, filename dikirim ke JS melalui HTML
        # JS kemudian akan mencoba memuat gambar dari /uploads/filename
        # Jadi kita perlu rute untuk /uploads/<filename> (lihat di bawah)
        # Redirect ke edit tidak diperlukan jika Anda memperbarui editor di halaman yang sama
        # Namun, jika editor.html adalah halaman terpisah, maka redirect ini benar.
        # Asumsi dari HTML Anda adalah editor muncul di halaman yang sama (index.html).
        # Jika begitu, upload seharusnya mengembalikan nama file atau path.
        # Mari kita ikuti alur JavaScript yang ada di HTML yang Anda berikan sebelumnya:
        # JavaScript di index.html melakukan fetch ke /upload, mengharapkan nama file kembali.
        return filename # Mengembalikan nama file ke JavaScript
    return "No file uploaded", 400


# Rute ini DIPERLUKAN untuk menampilkan gambar yang baru diunggah di preview
@app.route('/uploads/<filename>')
def send_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# Jika Anda menggunakan editor.html terpisah, rute ini relevan.
# Jika editor ada di index.html, rute ini mungkin tidak digunakan oleh JS yang Anda tunjukkan.
# @app.route('/edit/<filename>')
# def edit(filename):
#     return render_template('editor.html', filename=filename)

@app.route('/process/<filename>/<effect>')
def process(filename, effect):
    # Keamanan: Validasi nama file untuk mencegah path traversal
    if not filename or '/' in filename or '..' in filename:
        return "Invalid filename", 400

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    # Membuat nama file output yang unik atau sama, tergantung kebutuhan
    # Di sini kita menggunakan nama yang sama, menyimpannya di PROCESSED_FOLDER
    output_path = os.path.join(PROCESSED_FOLDER, filename)

    if not os.path.exists(input_path):
        return "Image not found in uploads", 404

    img = Image.open(input_path)

    if effect == 'grayscale':
        img = ImageOps.grayscale(img)
    elif effect == 'invert':
        img = ImageOps.invert(img.convert('RGB')) # Pastikan RGB untuk invert
    elif effect == 'mirror':
        img = ImageOps.mirror(img)
    elif effect == 'flip':
        img = ImageOps.flip(img)
    elif effect == 'blur':
        img = img.filter(ImageFilter.BLUR)
    elif effect == 'sharpen':
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0) # Faktor 2.0 mungkin terlalu kuat, bisa disesuaikan
    elif effect == 'brightness_up':
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5) # Faktor 1.5, bisa disesuaikan
    elif effect == 'contrast_up':
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5) # Faktor 1.5, bisa disesuaikan
    else:
        return "Effect not supported", 400

    img.save(output_path)
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Anda menggunakan port 5000 di screenshot