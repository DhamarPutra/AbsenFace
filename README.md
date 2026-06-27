# AbsenFace - Sistem Absensi Berbasis Pengenalan Wajah (Face Recognition)

AbsenFace adalah aplikasi sistem absensi mahasiswa berbasis pengenalan wajah (*face recognition*) real-time. Aplikasi ini mengintegrasikan antarmuka web modern berbasis **React** dengan server backend pemrosesan kecerdasan buatan berbasis **Python Flask** dan library **`face_recognition` (dlib ResNet)** untuk akurasi pencocokan wajah yang tinggi.

---

## 1. Product Requirements Document (PRD)

### A. Fitur Utama
1.  **Pendaftaran Wajah Baru (Registrasi Mahasiswa)**:
    *   Menginput data identitas mahasiswa (Nama, NIM, Peminatan).
    *   Mengambil sampel wajah berkualitas tinggi dengan mengunggah satu file gambar wajah mahasiswa.
    *   Ekstraksi wajah otomatis menggunakan jaringan saraf dlib untuk mengonversi wajah menjadi representasi vektor 128-dimensi (*face encoding*).
    *   Menyimpan data mahasiswa beserta data koordinat wajah ke dalam database SQLite secara terintegrasi.
2.  **Pemindaian Absensi Real-Time (Scan Absen)**:
    *   Mengakses kamera web (webcam) langsung di browser pengguna secara real-time.
    *   Menangkap gambar wajah (*snapshot*) secara berkala setiap 5 detik.
    *   Melakukan pencocokan koordinat wajah dengan database absensi secara real-time.
    *   Menampilkan status kehadiran beserta informasi identitas mahasiswa yang terdeteksi.

### B. Spesifikasi Teknis & Lingkungan Sistem
*   **Frontend**: React.js (Create React App), Tailwind CSS, React Webcam, Axios, React Router DOM.
*   **Backend**: Python 3.12/3.13, Flask (REST API), Flask-CORS, SQLite3, OpenCV, Pillow.
*   **Algoritma Kecerdasan Buatan**: dlib ResNet (via library `face_recognition`) dengan toleransi pencocokan (*match tolerance*) sebesar `0.5` untuk meminimalisir kesalahan identitas (*false positives*).
*   **Database**: SQLite (`server/mahasiswa.db`).

---

## 2. Struktur Proyek

```
FaceRecognition/
├── client/                 # Aplikasi Frontend (React)
│   ├── public/             # Aset publik statis
│   └── src/
│       ├── pages/          # Halaman Antarmuka Web
│       │   ├── api/        # Konfigurasi Endpoint API
│       │   │   └── port.js # URL API Server (default: http://127.0.0.1:5000/api)
│       │   ├── addMahasiswa.js # Form pendaftaran mahasiswa & wajah
│       │   └── scan.js     # Halaman scan absensi kamera
│       ├── App.js          # Konfigurasi Rute Web
│       └── index.js        # Entrypoint React
├── server/                 # Aplikasi Backend (Python Flask)
│   ├── DataSet/            # Folder penyimpanan foto wajah mahasiswa
│   ├── database.db         # Dump file SQL berisi data 70 mahasiswa (backup)
│   ├── mahasiswa.db        # Database SQLite biner asli (terbuat otomatis saat start)
│   ├── app.py              # Server Flask REST API utama
│   └── face_recognition.py # Skrip pengujian deteksi wajah lokal (Desktop OpenCV)
├── package.json            # Script manajemen proyek root (menggunakan concurrently)
└── README.md               # Dokumentasi Proyek
```

---

## 3. Langkah Setup Lingkungan (Setup Instructions)

Ikuti langkah-langkah di bawah ini untuk mempersiapkan lingkungan pengembangan di sistem operasi Windows Anda:

### A. Persiapan Dependensi Python & C++ Compiler
Karena library pengenalan wajah (`dlib`) dibangun menggunakan bahasa C++, sistem operasi Windows Anda membutuhkan kompiler C++ untuk menjalankannya.

1.  **Instalasi Python Resmi**:
    *   Unduh dan pasang **Python 3.12 atau 3.13** dari [python.org](https://www.python.org/downloads/).
    *   Pastikan Anda mencentang opsi **`Add python.exe to PATH`** saat memulai instalasi.
2.  **Instalasi Visual Studio Build Tools**:
    *   Unduh installer **Visual Studio Community** dari [visualstudio.microsoft.com/downloads/](https://visualstudio.microsoft.com/downloads/).
    *   Jalankan installer, lalu pilih beban kerja **`Desktop development with C++`** (Pengembangan desktop dengan C++).
    *   Klik **Install** dan tunggu hingga prosesnya selesai.
3.  **Instalasi Library Pendukung via CMD**:
    Buka Command Prompt baru (CMD) di direktori utama proyek, lalu jalankan perintah berikut secara berurutan:
    ```bash
    # 1. Upgrade pip ke versi terbaru
    python -m pip install --upgrade pip

    # 2. Downgrade setuptools (WAJIB untuk Python 3.13 mengatasi masalah pkg_resources)
    pip install "setuptools<70" wheel cmake

    # 3. Jalankan instalasi dlib menggunakan file precompiled wheel (jika ada) atau instal langsung:
    pip install dlib

    # 4. Install library Python pendukung lainnya
    pip install face_recognition flask flask-cors opencv-python numpy
    ```

### B. Persiapan Dependensi Node.js
Jalankan perintah berikut di direktori utama proyek untuk memasang dependensi Javascript:

1.  **Di Direktori Root** (untuk mengunduh library pelaksana paralel):
    ```bash
    npm install
    ```
2.  **Di Direktori Client** (untuk mengunduh modul React):
    ```bash
    cd client
    npm install
    cd ..
    ```

---

## 4. Cara Menjalankan Proyek (Run Instructions)

Setelah seluruh langkah setup selesai tanpa kendala, Anda dapat menjalankan frontend dan backend secara bersamaan menggunakan satu perintah terintegrasi:

### A. Menjalankan Server & Client Bersamaan (Sangat Direkomendasikan)
Di direktori root proyek Anda, jalankan perintah berikut di terminal:
```bash
npm run start
```
Perintah ini akan secara otomatis:
1.  Menjalankan backend Flask di alamat `http://127.0.0.1:5000`.
2.  Menginisialisasi database SQLite `server/mahasiswa.db` dari file SQL dump secara otomatis.
3.  Menjalankan frontend React di alamat `http://localhost:3000`.

### B. Menjalankan secara Terpisah (Opsional)
Jika Anda ingin memantau log secara terpisah, Anda dapat membuka dua jendela terminal:

*   **Terminal 1 (Backend Server)**:
    ```bash
    cd server
    python app.py
    ```
*   **Terminal 2 (Frontend Client)**:
    ```bash
    cd client
    npm start
    ```

---

## 5. Alur Pengujian & Verifikasi Aplikasi

Setelah aplikasi berjalan, silakan uji alur kerja sistem absensi wajah berikut ini di browser Anda:

1.  **Langkah 1: Daftarkan Wajah Mahasiswa Baru**:
    *   Buka halaman pendaftaran di: `http://localhost:3000/addMahasiswa`
    *   Masukkan data Nama, NIM, Peminatan, dan unggah foto wajah Anda dengan pencahayaan yang cukup.
    *   Klik **Add Face**. Server akan memproses foto tersebut dan menyimpan informasi wajah Anda ke dalam database.
2.  **Langkah 2: Lakukan Absensi Real-Time**:
    *   Buka halaman absensi di: `http://localhost:3000/scanAbsen`
    *   Izinkan akses kamera web di browser Anda.
    *   Hadapkan wajah ke kamera. Kamera akan mengambil cuplikan wajah setiap 5 detik secara berkala.
    *   Jika wajah Anda terdaftar di database, layar akan langsung menampilkan pesan sukses: **`Absen Berhasil: [Nama Anda] ([NIM Anda])`**.
3.  **Langkah 3: Uji Coba Desktop Lokal (Opsional)**:
    *   Anda juga dapat menjalankan skrip absensi versi desktop langsung di terminal server menggunakan perintah:
        ```bash
        python server/face_recognition.py
        ```
    *   Jendela OpenCV akan terbuka untuk melakukan pelacakan dan pelabelan nama wajah terdaftar Anda secara real-time dari kamera lokal.
