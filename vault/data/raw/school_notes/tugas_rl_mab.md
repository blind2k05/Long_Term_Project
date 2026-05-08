# Penerapan Multi-Armed Bandit (Reinforcement Learning)
Konteks: Tugas GSLC / Makalah Universitas Bina Nusantara (BINUS)
Mata Kuliah: Machine Learning & Reinforcement Learning

Tugas ini berfokus pada analisis kritis algoritma Reinforcement Learning, secara spesifik menggunakan pendekatan Multi-Armed Bandit (MAB).

## Studi Kasus: Optimasi Waktu Kontak
Studi kasus yang diangkat untuk paper ini adalah optimasi waktu kontak pelanggan. Bagaimana kita bisa menyeimbangkan antara eksplorasi (mencoba waktu kontak baru untuk melihat apakah pelanggan merespons) dan eksploitasi (menghubungi pelanggan di jam yang sudah terbukti memiliki tingkat respons tinggi). 

## Perbandingan: Thompson Sampling vs Epsilon-Greedy
- Konsep **Thompson Sampling** sangat cocok diterapkan di sini karena dapat secara dinamis menyesuaikan probabilitas keberhasilan berdasarkan *reward* (respons pelanggan) yang diperbarui secara *real-time*.
- Berbeda dengan metode **Epsilon-Greedy** yang melakukan eksplorasi secara acak (berdasarkan nilai *epsilon* statis), Thompson Sampling menggunakan distribusi probabilitas (biasanya *Beta distribution*). Hal ini membuatnya lebih cerdas dalam meminimalkan *regret* atau risiko membuang waktu menghubungi pelanggan di jam yang salah.

