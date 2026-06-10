=====================================
 📦 KNAPSACK SOLVER — README
 Desain & Analisa Algoritma (DAA)
 Semester 4 — UAS
=====================================

DESKRIPSI
---------
Aplikasi GUI untuk menyelesaikan Multi-Constraint 0/1 Knapsack Problem
menggunakan algoritma Dynamic Programming dengan dua batasan:
  - Berat (kg)
  - Volume (cm³) = panjang × lebar × tinggi

Nilai kepentingan tiap barang ditentukan melalui pop-up kuis 5 pertanyaan
bergaya neobrutalism.


CARA MENJALANKAN
----------------
1. Install tkinter jika belum ada (SYSTEM dependency, bukan pip):

   Arch Linux:
     sudo pacman -S tk

   Ubuntu/Debian:
     sudo apt-get install python3-tk

   Windows:
     Sudah otomatis terinstall bersama Python dari python.org

2. Jalankan aplikasi:

     python main.py   (Windows)
     python3 main.py  (Linux/WSL)

CATATAN: Tidak ada pip install yang dibutuhkan.
         requirements.txt kosong karena semua library
         (tkinter, logging, typing) adalah bawaan Python stdlib.


STRUKTUR FILE
-------------
  main.py       — GUI utama (neobrutalism, tkinter)
  dp_solver.py  — Algoritma DP multi-constraint
  quiz_popup.py — Pop-up kuis penilaian barang
  README.txt    — File ini


CARA PAKAI
----------
1. Isi nama, berat, dan dimensi (P × L × T) barang
2. Klik [+ TAMBAH BARANG] → muncul pop-up kuis 5 pertanyaan
3. Jawab Ya / Tidak → nilai barang tersimpan otomatis
4. Ulangi untuk semua barang
5. Isi kapasitas tas (berat maks + dimensi tas)
6. Klik [⚡ HITUNG SOLUSI] → hasil tampil di panel bawah
7. Klik [🔄 RESET] untuk mulai ulang


SISTEM PENILAIAN (KUIS)
-----------------------
Setiap "Ya" = +1 poin. Total skor = nilai barang (0–5).

  1. Apakah kamu pakai barang ini hampir setiap hari?
  2. Kalau barang ini ketinggalan, kamu bakal repot?
  3. Apakah barang ini susah dipinjam dari orang lain?
  4. Apakah kamu bakalan kangen barang ini kalau tidak dibawa?
  5. Kalau barang ini hilang, kamu perlu beli lagi secepatnya?


CONTOH DATA UJI
---------------
Kapasitas tas: berat maks 10 kg, dimensi 30×25×20 cm → vol 15.000 cm³

  No | Nama    | Berat | P×L×T       | Volume  | Nilai
  ---+---------+-------+-------------+---------+------
   1 | Buku    | 1 kg  | 20×15×3 cm  |  900    |  3
   2 | Botol   | 1 kg  | 8×8×25 cm   | 1.600   |  2
   3 | Sepatu  | 2 kg  | 30×15×12 cm | 5.400   |  4
   4 | Kamera  | 1.5kg | 12×8×6 cm   |  576    |  5
   5 | Jaket   | 1.5kg | 25×20×5 cm  | 2.500   |  3

Solusi optimal: Buku + Kamera + Jaket + Botol (atau sesuai hasil DP)


ALGORITMA
---------
Dynamic Programming — Multi-Constraint 0/1 Knapsack

  INISIALISASI: dp[0..n][0..W][0..V] = 0

  UNTUK setiap barang i dari 1 sampai n:
    UNTUK setiap kapasitas berat w dari 0 sampai W:
      UNTUK setiap kapasitas volume v dari 0 sampai V:
        JIKA berat[i] > w ATAU volume[i] > v:
          dp[i][w][v] = dp[i-1][w][v]
        LAIN:
          dp[i][w][v] = max(
            dp[i-1][w][v],
            dp[i-1][w-berat[i]][v-volume[i]] + nilai[i]
          )

  Kompleksitas Waktu : O(n × W × V)
  Kompleksitas Ruang : O(n × W × V)

=====================================
