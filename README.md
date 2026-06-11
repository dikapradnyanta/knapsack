# Knapsack Solver

**Desain & Analisa Algoritma (DAA)**
**Semester 4 — UAS**

---

## Deskripsi

Aplikasi antarmuka grafis (GUI) untuk menyelesaikan **Multi-Constraint 0/1 Knapsack Problem** menggunakan tiga pilihan algoritma: Dynamic Programming, Brute Force, dan Greedy. Aplikasi ini mempertimbangkan dua batasan kapasitas:
- **Berat** (dalam satuan kg)
- **Volume** (dalam satuan cm³, dihitung dari panjang × lebar × tinggi)

Pengguna dapat menonaktifkan salah satu atau kedua batasan tersebut jika diinginkan. Nilai atau bobot kepentingan dari masing-masing barang didapatkan melalui survei pertanyaan interaktif.

---

## Fitur Utama

- **Tiga Metode Penyelesaian:** Perbandingan komputasi langsung antara Dynamic Programming, Greedy, dan Brute Force.
- **Fleksibilitas Batasan:** Pengguna bisa mengabaikan batasan berat atau volume melalui kotak centang (checkbox).
- **Impor dan Ekspor CSV:** Kemampuan menyimpan daftar barang ke dalam format CSV, serta memuat kembali data dari CSV untuk mempermudah skenario pengujian massal.
- **Pengukuran Waktu Eksekusi:** Menampilkan durasi eksekusi dari setiap algoritma (dalam milidetik) untuk membantu mahasiswa menganalisis performa algoritma.
- **Animasi Visualisasi:** Simulasi penempatan barang yang terpilih dan proporsi penggunaan tas di panel hasil.

---

## Cara Menjalankan

1. **Instalasi Dependensi Python:**
   Proyek ini menggunakan pustaka pihak ketiga (seperti `pygame` untuk audio latar). Jalankan perintah berikut pada terminal/Command Prompt:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Instalasi Tkinter:**
   Library antarmuka grafis Tkinter umumnya sudah terpasang secara otomatis jika Anda menginstal Python di Windows. Bagi pengguna sistem operasi lain:
   - **Ubuntu/Debian:** `sudo apt-get install python3-tk`
   - **Arch Linux:** `sudo pacman -S tk`

3. **Menjalankan Aplikasi:**
   Ketik perintah berikut pada terminal di dalam folder direktori proyek:
   ```cmd
   python main.py
   ```

---

## Struktur File

- `main.py` — Program utama beserta antarmuka pengguna grafis.
- `dp_solver.py` — Modul pustaka penyelesaian algoritma Dynamic Programming.
- `greedy_solver.py` — Modul pustaka penyelesaian algoritma Greedy.
- `bf_solver.py` — Modul pustaka penyelesaian algoritma Brute Force.
- `quiz_popup.py` — Modul antarmuka kuis untuk penentuan skor prioritas barang.
- `contoh_barang.csv` — File data contoh untuk menguji fungsionalitas impor data.

---

## Panduan Penggunaan

1. **Memasukkan Barang:** Isi kolom nama barang, berat, dan dimensi secara lengkap (P × L × T).
2. **Evaluasi Nilai:** Klik tombol 'Input Barang'. Sebuah pop-up kuis berisi 5 pertanyaan akan muncul. Setiap jawaban 'Ya' menyumbang +1 poin pada nilai barang (skala 0 sampai 5).
3. **Manipulasi Data:** Gunakan tombol 'Import CSV' atau 'Export CSV' pada bagian tengah untuk menyimpan profil simulasi atau memuat kasus ujian secara otomatis.
4. **Penentuan Kapasitas:** Di sisi sebelah kanan, tetapkan batas maksimal berat dan dimensi ruang tas. Hapus centang kotak 'Aktif' jika Anda ingin melepaskan batasan terkait.
5. **Menghitung Solusi:** Pilih satu dari tiga algoritma yang tersedia di bagian kanan bawah:
   - **Solusi Optimal (DP):** Metode andalan utama untuk mencari titik maksimal.
   - **Greedy:** Metode heuristik prioritas urutan.
   - **Brute Force:** Pengecekan kombinatorik absolut (hanya direkomendasikan bila data barang di bawah 20 item).
6. **Interpretasi Hasil:** Hasil perolehan nilai, rincian barang, serta rekam waktu eksekusi komputasi akan terpampang di panel bawah. Klik tombol 'Lihat Solusi' untuk melihat rincian alokasi tas.

---

## Skenario Pengujian Data (Best Case & Worst Case)

Setiap algoritma yang diimplementasikan pada aplikasi ini memiliki kelebihan dan titik lemahnya masing-masing. Berikut adalah pedoman pengujian untuk memahami karakteristik performanya:

### 1. Dynamic Programming (DP)
- **Best Case:** Terjadi ketika kapasitas tas (Berat dan Volume) disetel pada angka yang moderat. Karena matriks memori yang dibentuk berukuran kecil, DP akan memberikan solusi 100% optimal dalam waktu instan dengan penggunaan RAM di bawah 5 MB.
- **Worst Case:** Terjadi apabila kapasitas tas disetel ke angka yang sangat ekstrem (contoh: volume ratusan ribu cm³) tanpa batasan resolusi. Hal ini memaksa algoritma mengalokasikan jutaan sel matriks di dalam memori, sehingga waktu komputasi bisa melambat hingga beberapa detik dan memakan RAM secara besar-besaran (Space-Time Tradeoff).

### 2. Algoritma Greedy
- **Best Case:** Terjadi apabila barang-barang dengan rasio nilai tertinggi secara kebetulan memiliki ukuran yang pas untuk mengisi penuh tas tanpa menyisakan celah kosong. Greedy akan menyelesaikan kalkulasi nyaris dalam 0.00 milidetik (memori nyaris 0 MB) sambil memberikan solusi yang menyerupai tingkat optimalitas DP.
- **Worst Case:** Terjadi saat ada suatu barang dengan ukuran raksasa namun memiliki nilai yang cukup tinggi. Greedy akan memprioritaskan barang tersebut hingga menghabiskan seluruh sisa tas, padahal ruang tersebut sejatinya bisa diisi oleh lima barang kecil lain yang bila diakumulasi nilainya jauh mengalahkan barang raksasa tersebut. Hasil komputasinya sangat tidak optimal.

### 3. Algoritma Brute Force
- **Best Case:** Terjadi saat jumlah data barang yang dimasukkan relatif sedikit (kisaran 1 hingga 15 barang). Komputer akan menyelesaikan pencarian secara menyeluruh dalam sekedip mata, memberikan jaminan solusi 100% optimal dengan beban memori yang jauh lebih ringan dibanding DP.
- **Worst Case:** Terjadi bila pengguna mencoba menganalisis kumpulan data berskala besar (contoh: 30 hingga 50 barang ke atas). Karena waktu eksekusi bertumbuh secara eksponensial (O(2^N)), komputasi 40 barang akan menuntut evaluasi atas lebih dari 1 Triliun kombinasi. Aplikasi akan mengalami *freeze* atau *hang* hingga hitungan hari.

---

## Penjelasan Algoritma

1. **Dynamic Programming (Kompleksitas: O(N × W × V))**
   Algoritma ini beroperasi dengan membagi masalah ke dalam sub-masalah secara bertahap dan mencatat nilainya dalam struktur matriks berdimensi tiga (jumlah barang, bobot, dan volume). Memiliki kompleksitas *pseudo-polynomial*, sehingga kepastian perolehan nilai optimal sangat dijamin meskipun mungkin melambat saat kapasitas batasan di set ke angka yang tinggi.

2. **Greedy (Kompleksitas: O(N log N))**
   Metodologi sederhana di mana daftar barang diurutkan secara menurun berdasarkan nilai kepentingannya, kemudian barang dimasukkan berturut-turut asalkan kapasitas tas masih mencukupi. Sifat algoritma yang *greedy* membuatnya berkecepatan komputasi nyaris instan, tetapi hasil akhirnya seringkali bersifat tidak optimal karena tidak mampu menganalisis kombinasi sisa ruang dengan efisien.

3. **Brute Force (Kompleksitas: O(2^N))**
   Mencoba, mengevaluasi, dan mencocokkan setiap sub-kombinasi kumpulan barang secara manual dari awal hingga akhir. Brute Force tidak dapat tertipu oleh jebakan heuristik sehingga hasil yang diberikan pasti 100% optimal. Namun, skalabilitasnya yang bersifat eksponensial menyebabkan komputer akan *freeze* jika menghadapi variasi data dalam kuantitas banyak.
