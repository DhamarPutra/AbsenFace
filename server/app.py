import os
import re
import json
import base64
import sqlite3
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition

app = Flask(__name__)
CORS(app)  # Mengizinkan request dari frontend React (port 3000)

DB_PATH = 'server/mahasiswa.db'
SQL_DUMP_PATH = 'server/database.db'
DATASET_DIR = 'server/DataSet'

# Membuat direktori DataSet jika belum ada
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

def init_db():
    """Inisialisasi database SQLite dan populate data dari SQL dump jika kosong."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buat tabel mahasiswa
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mahasiswa (
        id_isc TEXT PRIMARY KEY,
        nama_mahasiswa TEXT,
        nim TEXT UNIQUE,
        peminatan TEXT
    )
    """)
    
    # Buat tabel face encodings untuk menyimpan data wajah 128-dimensi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS face_encodings (
        nim TEXT PRIMARY KEY,
        encoding TEXT,
        FOREIGN KEY(nim) REFERENCES mahasiswa(nim)
    )
    """)
    conn.commit()
    
    # Periksa apakah data mahasiswa sudah di-populate
    cursor.execute("SELECT COUNT(*) FROM mahasiswa")
    count = cursor.fetchone()[0]
    
    if count == 0 and os.path.exists(SQL_DUMP_PATH):
        print("Populating SQLite database dari SQL dump database.db...")
        try:
            with open(SQL_DUMP_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Membersihkan penulisan tanda petik ganda SQL yang tidak standar
            content_cleaned = content.replace("''", "")
            
            # Match pola baris insert: ('ISC...', 'Nama...', 'NIM...', 'Peminatan...')
            pattern = r"\('([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\)"
            matches = re.findall(pattern, content_cleaned)
            
            inserted_count = 0
            for id_isc, nama, nim, peminatan in matches:
                cursor.execute("""
                INSERT OR IGNORE INTO mahasiswa (id_isc, nama_mahasiswa, nim, peminatan)
                VALUES (?, ?, ?, ?)
                """, (id_isc, nama, nim, peminatan))
                inserted_count += 1
                
            conn.commit()
            print(f"Sukses memasukkan {inserted_count} data mahasiswa dari SQL dump ke SQLite.")
        except Exception as e:
            print("Gagal mempopulasi database:", e)
            
    conn.close()

# Jalankan inisialisasi database saat server Flask pertama kali berjalan
init_db()

@app.route('/api/add_user', methods=['POST'])
def add_user():
    """
    Endpoint untuk mendaftarkan wajah mahasiswa baru.
    Menerima data form-data: nama, nim, peminatan, dan file image.
    """
    try:
        nama = request.form.get('nama')
        nim = request.form.get('nim')
        peminatan = request.form.get('peminatan')
        image_file = request.files.get('image')
        
        if not all([nama, nim, peminatan, image_file]):
            return jsonify({"error": "Semua field (nama, nim, peminatan, image) wajib diisi"}), 400
            
        # Simpan file gambar sementara ke folder DataSet
        file_extension = os.path.splitext(image_file.filename)[1]
        temp_image_path = os.path.join(DATASET_DIR, f"{nim}{file_extension}")
        image_file.save(temp_image_path)
        
        # Load gambar menggunakan face_recognition
        try:
            loaded_image = face_recognition.load_image_file(temp_image_path)
            encodings = face_recognition.face_encodings(loaded_image)
        except Exception as e:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return jsonify({"error": f"Gagal membaca format gambar: {str(e)}"}), 400
            
        # Validasi deteksi wajah
        if len(encodings) == 0:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return jsonify({"error": "Wajah tidak terdeteksi pada gambar. Silakan upload foto wajah yang lebih jelas."}), 400
            
        if len(encodings) > 1:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return jsonify({"error": "Terdeteksi lebih dari satu wajah. Harap upload foto dengan satu wajah saja."}), 400
            
        # Ambil encoding wajah pertama (128-dimensional array)
        face_encoding = encodings[0]
        encoding_json = json.dumps(face_encoding.tolist())
        
        # Simpan/update data ke database SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tentukan id_isc otomatis atau menggunakan default
        cursor.execute("SELECT id_isc FROM mahasiswa WHERE nim=?", (nim,))
        existing_student = cursor.fetchone()
        if existing_student:
            id_isc = existing_student[0]
        else:
            # Generate ID baru berdasarkan jumlah mahasiswa saat ini
            cursor.execute("SELECT COUNT(*) FROM mahasiswa")
            current_count = cursor.fetchone()[0]
            id_isc = f"ISC24{str(current_count + 1).zfill(5)}"
            
        # Insert/Replace data mahasiswa
        cursor.execute("""
        INSERT OR REPLACE INTO mahasiswa (id_isc, nama_mahasiswa, nim, peminatan)
        VALUES (?, ?, ?, ?)
        """, (id_isc, nama, nim, peminatan))
        
        # Insert/Replace encoding wajah
        cursor.execute("""
        INSERT OR REPLACE INTO face_encodings (nim, encoding)
        VALUES (?, ?)
        """, (nim, encoding_json))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Data mahasiswa dan wajah berhasil disimpan!",
            "student": {
                "id_isc": id_isc,
                "nama": nama,
                "nim": nim,
                "peminatan": peminatan
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan server: {str(e)}"}), 500

@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    Endpoint untuk mendeteksi absensi wajah secara real-time.
    Menerima form-data: image_data (base64 string dari webcam React).
    """
    try:
        image_data_base64 = request.form.get('image_data')
        if not image_data_base64:
            return jsonify({"error": "Data gambar (image_data) kosong"}), 400
            
        # Menghapus prefix data:image/jpeg;base64 jika ada
        if ',' in image_data_base64:
            image_data_base64 = image_data_base64.split(',')[1]
            
        # Decode base64 menjadi array OpenCV
        try:
            img_bytes = base64.b64decode(image_data_base64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({"error": "Gagal mendekode gambar"}), 400
                
            # Konversi BGR (OpenCV) ke RGB (face_recognition)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            return jsonify({"error": f"Gagal memproses gambar: {str(e)}"}), 400
            
        # Temukan lokasi wajah dan hitung encoding-nya
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        if len(face_encodings) == 0:
            return jsonify({"message": "Wajah tidak terdeteksi. Dekatkan wajah Anda ke kamera."}), 200
            
        # Ambil semua data encoding wajah dari database SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nim, encoding FROM face_encodings")
        db_rows = cursor.fetchall()
        
        if len(db_rows) == 0:
            conn.close()
            return jsonify({"message": "Belum ada wajah terdaftar di database absensi."}), 200
            
        # Siapkan data pencocokan
        known_nims = []
        known_encodings = []
        for nim, enc_str in db_rows:
            known_nims.append(nim)
            known_encodings.append(np.array(json.loads(enc_str)))
            
        # Lakukan pencocokan (gunakan wajah pertama yang terdeteksi)
        current_face_encoding = face_encodings[0]
        
        # dlib compare_faces dengan toleransi kecocokan 0.5 (semakin kecil semakin ketat)
        matches = face_recognition.compare_faces(known_encodings, current_face_encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(known_encodings, current_face_encoding)
        
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                matched_nim = known_nims[best_match_index]
                
                # Ambil info lengkap mahasiswa dari DB
                cursor.execute("SELECT nama_mahasiswa, peminatan FROM mahasiswa WHERE nim=?", (matched_nim,))
                student_info = cursor.fetchone()
                conn.close()
                
                if student_info:
                    nama_mahasiswa, peminatan = student_info
                    return jsonify({
                        "message": f"Absen Berhasil: {nama_mahasiswa} ({matched_nim})",
                        "status": "success",
                        "data": {
                            "nama": nama_mahasiswa,
                            "nim": matched_nim,
                            "peminatan": peminatan
                        }
                    }), 200
                    
        conn.close()
        return jsonify({"message": "Wajah tidak terdaftar dalam database absensi."}), 200
        
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan server saat pemindaian: {str(e)}"}), 500

if __name__ == '__main__':
    # Jalankan server di localhost port 5000 sesuai konfigurasi client port.js
    app.run(host='127.0.0.1', port=5000, debug=True)
