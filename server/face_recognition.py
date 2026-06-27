import cv2
import sqlite3
import json
import numpy as np
import face_recognition

# 1. Koneksi ke database SQLite untuk mengambil data wajah terdaftar
DB_PATH = 'server/mahasiswa.db'

def load_known_faces():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ambil data mahasiswa dan encoding wajah
    cursor.execute("""
        SELECT mahasiswa.nim, mahasiswa.nama_mahasiswa, face_encodings.encoding 
        FROM face_encodings 
        JOIN mahasiswa ON face_encodings.nim = mahasiswa.nim
    """)
    rows = cursor.fetchall()
    conn.close()
    
    known_nims = []
    known_names = []
    known_encodings = []
    
    for nim, name, enc_str in rows:
        known_nims.append(nim)
        known_names.append(name)
        known_encodings.append(np.array(json.loads(enc_str)))
        
    return known_nims, known_names, known_encodings

print("Memuat data wajah dari SQLite...")
try:
    known_nims, known_names, known_encodings = load_known_faces()
    print(f"Sukses memuat {len(known_names)} wajah terdaftar.")
except Exception as e:
    print("Gagal memuat database (Pastikan Anda sudah menjalankan server/app.py terlebih dahulu untuk inisialisasi):", e)
    known_nims, known_names, known_encodings = [], [], []

# 2. Inisialisasi Kamera
camera = 0
video = cv2.VideoCapture(camera, cv2.CAP_DSHOW)

print("Menjalankan kamera... Tekan 'q' untuk keluar.")

while True:
    check, frame = video.read()
    if not check:
        print("Gagal mengakses kamera.")
        break
        
    # Perkecil ukuran frame (opsional, untuk mempercepat pemrosesan)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
    # Konversi BGR (OpenCV) ke RGB (face_recognition)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Deteksi lokasi wajah dan encoding wajah di frame saat ini
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Kembalikan koordinat ke ukuran frame asli (dikali 4 karena tadi diresize 0.25)
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        
        name = "Tidak Dikenal"
        
        # Lakukan pencocokan jika ada wajah terdaftar
        if len(known_encodings) > 0:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    
        # Gambar kotak di sekitar wajah
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Tulis nama di bawah wajah
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
        
    # Tampilkan jendela output
    cv2.imshow("Face Recognition Absen (Local Test)", frame)
    
    # Tekan 'q' untuk berhenti
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

video.release()
cv2.destroyAllWindows()