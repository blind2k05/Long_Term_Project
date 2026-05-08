# Implementasi Fitur Top-Up Game & Database Transaction
Konteks: Proyek Website Top-Up Game (Laravel)

## Setup Database & Relasi
- File *Migrations* dan *Seeders* sudah berhasil dikonfigurasi untuk tabel `Users`, `Transactions`, dan `GameItems`.
- Relasi *Eloquent* antar tabel sudah dipastikan aman dan saling terhubung sebelum masuk ke logika controller.

## Logika Controller & Proteksi Saldo
Salah satu tantangan utama adalah memastikan integritas transaksi di database. Saat user melakukan top-up, sistem harus membungkus proses pemotongan saldo dan update status ke dalam `DB::beginTransaction()`. 
Jika API pembayaran pihak ketiga gagal merespons atau terjadi error di tengah proses, transaksi harus di-`rollback` untuk mencegah saldo user terpotong tanpa mendapatkan item in-game. 

## Sistem Notifikasi
Fitur notifikasi sukses dan gagal sudah diimplementasikan di *frontend* untuk memberikan *feedback* langsung ke user setelah transaksi berhasil diproses oleh *controller*.