# Chunking Experiment Lab

- Total documents: 3 files (.md)
- Total words: ~250 words
- Embedding model used: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Evaluation method: manual relevance judgment
- Chunk Size Tested: 500 characters
- Chunk Overlap Tested: 50 characters

## Table Results :

| Document Source | Chunk ID | Chunk Text Snippet (First 100 chars) | Evaluation Note | Status |
| :--- | :--- | :--- | :--- | :--- |
| `evaluasi_xgboost_churn.md` | Chunk 1 | `# Evaluasi Model Telco Churn... Pada iterasi awal, kita menggunakan algoritma Random Forest...` | Sempurna. Konteks masalah (Recall rendah pada Random Forest) tertangkap utuh dalam satu chunk. | ✅ Pass |
| `evaluasi_xgboost_churn.md` | Chunk 2 | `...berhenti berlangganan. Sebagai langkah perbaikan, kita melakukan transisi ke XGBoost...` | Cukup baik. overlap 50 karakter berhasil menjaga konteks alasan pindah ke XGBoost. | ✅ Pass |
| `tugas_rl_mab.md` | Chunk 1 | `# Penerapan Multi-Armed Bandit... Tugas ini berfokus pada analisis kritis algoritma...` | Sempurna. Informasi tentang BINUS dan tugas makalah langsung terikat dengan teori MAB. | ✅ Pass |
| `laravel_topup_system.md` | Chunk 1 | `# Implementasi Fitur Top-Up Game... Logika controller untuk website top-up game ini berpusat...` | Kalimat penjelasan DB Transaction sedikit terpotong di akhir chunk. | ⚠️ Warning |

**Kesimpulan Evaluasi Sementara:**
Ukuran *chunk* 500 karakter sudah cukup baik untuk menangkap konteks dasar. Namun, untuk dokumen teknis (*coding notes*) yang kalimatnya panjang-panjang, ukuran 500 karakter berisiko memotong logika kode di tengah jalan. 

**Rekomendasi:** 
Bisa dicoba untuk menaikkan `CHUNK_SIZE` menjadi 700 atau 800 agar instruksi *coding* bisa masuk secara utuh ke dalam satu vektor.