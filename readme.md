## Explanation of the project
Proyek **Second Brain** ini adalah asisten kecerdasan buatan berbasis RAG (*Retrieval-Augmented Generation*) yang berjalan **100% secara lokal (offline)**. Sistem ini dirancang untuk membaca, mengingat, dan menjawab pertanyaan berdasarkan catatan pribadi, jurnal harian, dan dokumen PDF pengguna. Proyek ini sangat menjaga privasi (Privacy-Preserving) dan tidak berbayar (Zero-Cost Inference) karena menggunakan model *embedding* lokal (Sentence-Transformers) dan LLM lokal (Gemma 2B via Ollama) tanpa mengirimkan data apa pun ke internet.

## Data sources
Data mentah disimpan di dalam direktori `vault/data/raw/` yang terbagi menjadi beberapa kategori:
- **Journal entries (X docs):** Berisi catatan harian dan minat pribadi, seperti *update* aktivitas *gaming* (Elden Ring, Monster Hunter) dan eksplorasi sejarah *pro-wrestling* (era NJPW Inoki Dark Ages).
- **School notes (Y docs):** Berisi materi perkuliahan dan draf makalah, seperti catatan tentang algoritma *Reinforcement Learning* (perbandingan Thompson Sampling vs Epsilon-Greedy).
- **Internship meetings (Z docs):** Berisi catatan teknis selama magang, seperti evaluasi model *Machine Learning* (implementasi XGBoost untuk Telco Churn).
- **Coding notes (W docs):** Berisi dokumentasi rekayasa perangkat lunak, seperti logika *controller* dan transaksi database untuk sistem top-up game berbasis Laravel.

## Setup
- **Python version:** Disarankan menggunakan Python 3.9 atau yang lebih baru.
- **Persyaratan Sistem:**
  1. Pastikan aplikasi [Ollama](https://ollama.com/) sudah terinstal dan berjalan di sistem operasi Anda.
  2. Pastikan model bahasa sudah diunduh ke dalam Ollama dengan menjalankan: `ollama run gemma2:2b`.
- **Instalasi:**
  Jalankan perintah berikut di terminal untuk menginstal semua *library* yang dibutuhkan:
  pip install -r requirements.txt

## Ingesting documents

**Cara menjalankan:**
Pastikan Anda berada di root direktori proyek, lalu eksekusi perintah berikut di terminal:
python ingest.py
**Apa yang dilakukannya:**
Skrip `ingest.py` berfungsi sebagai jalur penyerapan data (*data pipeline*). Proses yang terjadi di balik layar adalah:
1. Membaca seluruh dokumen mentah (mendukung format `.md`, `.txt`, dan `.pdf`) yang berada di dalam folder `vault/data/raw/`.
2. Memecah teks dari dokumen-dokumen tersebut menjadi potongan-potongan kecil (*chunking*) menggunakan `RecursiveCharacterTextSplitter` dari LangChain.
3. Mengonversi teks menjadi representasi vektor matematis menggunakan model *embedding* (Sentence-Transformers).
4. Menyimpan data vektor tersebut secara permanen ke dalam basis data vektor lokal (ChromaDB) yang terletak di direktori `vault/chroma_db/`.

## Searching

- **Cara menjalankan `search.py`:**
python search.py
- **Example query + output:**
Apa keunggulan Thompson Sampling?

AI: Berdasarkan catatan, Thompson Sampling unggul karena dapat secara dinamis menyesuaikan probabilitas keberhasilan berdasarkan reward yang diperbarui secara real-time. Hal ini membuatnya lebih cerdas dalam meminimalkan regret dibandingkan dengan metode Epsilon-Greedy.

## Configuration
Anda dapat mengubah pengaturan inti dari sistem pencarian dan pemrosesan teks di dalam file `config.py`:

- **`CHUNK_SIZE`**: Menentukan batas jumlah maksimal karakter dalam satu potongan teks (chunk). Ukuran yang pas memastikan AI tidak menerima terlalu banyak atau terlalu sedikit konteks bacaan sekaligus.
- **`CHUNK_OVERLAP`**: Menentukan jumlah karakter yang diulang atau tumpang-tindih (overlap) di antara dua teks yang terpotong. Hal ini berfungsi sebagai "jembatan" agar tidak ada kalimat atau makna yang terputus secara mendadak.
- **`TOP_K`**: Menentukan jumlah dokumen referensi teratas yang paling relevan yang akan diekstrak dari ChromaDB dan diberikan kepada AI sebagai dasar untuk menjawab pertanyaan.
- **`EMBEDDING_MODEL_NAME`**: Menentukan model *embedding* yang digunakan (bisa diatur menggunakan *path* folder model lokal untuk mode 100% *offline* atau nama model dari HuggingFace).

## Troubleshooting & Kapan Harus Menjalankan Ingest Ulang

Sistem database vektor tidak diperbarui secara otomatis. Anda **TIDAK PERLU** menjalankan `ingest.py` setiap kali ingin bertanya kepada AI. Skrip `ingest.py` HANYA perlu dijalankan apabila terjadi salah satu dari 4 skenario berikut:

1. **Ada penambahan file dokumen baru** (PDF/MD/TXT) ke dalam folder `vault/data/raw/`.
2. **Ada pengeditan/perubahan isi teks** pada dokumen lama yang sudah ada.
3. **Mengubah parameter `CHUNK_SIZE` atau `CHUNK_OVERLAP`** di dalam `config.py`.
4. **Mengubah model *embedding*** (berpindah dari model *online* ke *offline*, atau sebaliknya).

**Solusi Error: AI Gagal Menemukan Konteks / Hasil Kosong**
Jika Anda bertanya tentang suatu hal yang pasti ada di dalam catatan, tetapi AI menjawab *"Maaf, informasi tidak ditemukan"*, kemungkinan besar terjadi *bentrokan vektor* (dimensi matriks berbeda karena perubahan model atau *chunking*). 

**Cara Mengatasinya (Hard Reset):**
1. Buka *File Explorer*, cari dan **HAPUS** folder `vault/chroma_db` secara manual beserta seluruh isinya.
2. Buka terminal, lalu jalankan ulang perintah `python ingest.py`.
3. Tunggu hingga proses penyerapan selesai. Database Anda kini sudah kembali bersih dan disinkronkan dengan konfigurasi terbaru.