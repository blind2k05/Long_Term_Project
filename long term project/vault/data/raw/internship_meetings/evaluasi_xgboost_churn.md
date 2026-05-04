# Evaluasi Model Telco Churn dengan XGBoost
Topik: Prediksi Churn Pelanggan (IBM Telco Dataset)
Lokasi: Telkomsel Smart Office (TSO)

## Iterasi Model Dasar
Pada iterasi awal, kita menggunakan algoritma Random Forest untuk memprediksi pelanggan yang akan churn. Namun, hasil evaluasi menunjukkan bahwa metrik Recall pada base model tersebut masih terlalu rendah. Artinya, model kita masih sering kelewatan (false negative) dalam mendeteksi pelanggan yang sebenarnya berniat untuk berhenti berlangganan.

## Transisi ke XGBoost & Feature Engineering
Sebagai langkah perbaikan, kita melakukan transisi ke algoritma XGBoost. XGBoost dipilih karena kemampuannya menangani imbalance data dengan lebih baik melalui parameter `scale_pos_weight`. 
- Proses *data cleaning* dan *feature engineering* menggunakan `Pandas` dan `Scikit-learn` (terutama untuk mengekstrak fitur dari data RFM) terbukti solid. 
- Fokus selanjutnya: Melakukan *hyperparameter tuning* pada XGBoost untuk menaikkan skor Recall tanpa terlalu mengorbankan Precision.

## Diskusi Mentor (TSO)
Catatan dari diskusi rutin dengan mentor: Perlu memperdalam optimasi SQL dan praktik terbaik integrasi *Big Data*. Hal ini penting agar proses penarikan (*query*) data mentah pelanggan dari database perusahaan bisa berjalan lebih cepat dan efisien sebelum masuk ke pipeline *Machine Learning*.