# Chunking Experiment Lab

## Iterasi 1: Pengujian Parameter Dasar
- **Total documents:** 3 files (.md)
- **Total words:** ~250 words
- **Embedding model used:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Chunk Size Tested:** 500 characters
- **Chunk Overlap Tested:** 50 characters

### Hasil Evaluasi (Iterasi 1):

| Document Source | Chunk ID | Chunk Text Snippet (First 100 chars) | Evaluation Note | Status |
| :--- | :--- | :--- | :--- | :--- |
| `evaluasi_xgboost_churn.md` | Chunk 1 | `# Evaluasi Model Telco Churn... Pada iterasi awal, kita menggunakan algoritma Random Forest...` | Sempurna. Konteks masalah (Recall rendah pada Random Forest) tertangkap utuh dalam satu chunk. | ✅ Pass |
| `evaluasi_xgboost_churn.md` | Chunk 2 | `...berhenti berlangganan. Sebagai langkah perbaikan, kita melakukan transisi ke XGBoost...` | Cukup baik. overlap 50 karakter berhasil menjaga konteks alasan pindah ke XGBoost. | ✅ Pass |
| `tugas_rl_mab.md` | Chunk 1 | `# Penerapan Multi-Armed Bandit... Tugas ini berfokus pada analisis kritis algoritma...` | Sempurna. Informasi tentang BINUS dan tugas makalah langsung terikat dengan teori MAB. | ✅ Pass |
| `laravel_topup_system.md` | Chunk 1 | `# Implementasi Fitur Top-Up Game... Logika controller untuk website top-up game ini berpusat...` | Kalimat penjelasan DB Transaction sedikit terpotong di akhir chunk. | ⚠️ Warning |

**Kesimpulan Sementara:** Ukuran *chunk* 500 karakter berisiko memotong logika kode atau kalimat teknis di tengah jalan. Overlap 50 karakter terlalu sempit untuk menjaga keutuhan konteks antar-paragraf.

---

## Iterasi 2: Arsitektur Hybrid & Pemrosesan Tabular (Current State)
- **Embedding model used:** `BAAI/bge-m3` (Mendukung konteks multilingual yang lebih dalam)
- **Chunk Size Tested:** 1000 characters
- **Chunk Overlap Tested:** 200 characters
- **New Feature:** Row-to-Text Stringification untuk file `.csv`
- **Sanity Filter (Relevancy):** `MIN_SCORE = 0.45`

### Hasil Evaluasi (Iterasi 2):

| Document Source | Format | Uji Coba Kueri (Prompt) | Evaluation Note | Status |
| :--- | :--- | :--- | :--- | :--- |
| `laravel_topup_system.md` | Markdown | Ekstraksi alur fungsi *TransactionController* | Ukuran chunk 1000 sukses merangkul seluruh blok logika PHP tanpa terpotong. Konteks aman. | ✅ Pass |
| `sample_site_data.csv` | CSV | "Apa RAT dan kapasitas gbps dari BTS Tunjungan?" | LLM (Gemma 2B) sukses mengekstrak baris tabular ("5G NR" & "12.5") berkat teknik *Stringification*. Tidak perlu Pandas eksekusi di sisi inferensi. | ✅ Pass |
| *Negative Testing* | N/A | "Siapa nama teknisi BTS Gatot Subroto?" | Sistem berhasil menolak halusinasi ("Maaf, informasi tidak ditemukan") berkat implementasi batas ambang skor 45%. | ✅ Pass |

**Kesimpulan Akhir:** Kombinasi `CHUNK_SIZE` 1000 dan `CHUNK_OVERLAP` 200 adalah *sweet spot* (titik ideal) untuk dokumen teknis dan operasional. Implementasi teknik *stringification* terbukti sangat tangguh untuk memasukkan data terstruktur (CSV) ke dalam *Vector Database* tanpa merusak pemahaman LLM lokal.