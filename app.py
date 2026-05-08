import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import config
import ollama
import os
import subprocess
import shutil  

# Buat folder jika belum ada
os.makedirs(os.path.join("vault", "data", "raw"), exist_ok=True)

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Second Brain AI", page_icon="🧠", layout="centered")

# === SIDEBAR ===
with st.sidebar:
    st.header("📂 Tambah Catatan Baru")
    st.write("Drag & Drop file ke sini untuk memasukkannya ke otak AI.")
    
    uploaded_file = st.file_uploader("Pilih file PDF, TXT, atau MD", type=["pdf", "txt", "md"])
    
    if uploaded_file is not None:
        save_path = os.path.join("vault", "data", "raw", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ '{uploaded_file.name}' tersimpan!")
        
        if st.button("🧠 Proses Tambahan (Soft Update)"):
            with st.spinner("Sedang memproses dokumen..."):
                try:
                    subprocess.run(["python", "ingest.py"], check=True)
                    st.cache_resource.clear()
                    st.success("Selesai diproses!")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

    # --- FITUR BARU: TOMBOL HARD RESET OTOMATIS ---
    st.divider() # Garis pembatas
    st.header("🛠️ Troubleshooting")
    st.caption("Gunakan tombol ini jika AI gagal membaca file baru (Terjadi bentrok/Windows Lock).")
    
    if st.button("🔴 Hard Reset & Bangun Ulang Memori"):
        with st.spinner("Menghapus database lama dan memproses ulang seluruh data..."):
            try:
                # 1. Lepaskan "gembok" memori dari Streamlit
                st.cache_resource.clear()
                
                # 2. Hapus folder chroma_db secara otomatis
                if os.path.exists(config.CHROMA_PATH):
                    shutil.rmtree(config.CHROMA_PATH, ignore_errors=True)
                
                # 3. Jalankan ulang ingest.py
                subprocess.run(["python", "ingest.py"], check=True)
                
                st.success("Hard Reset Berhasil! Database AI sudah bersih dan sinkron.")
                st.rerun() # Refresh halaman web otomatis
            except Exception as e:
                st.error(f"Gagal melakukan reset: {e}")
# ===============================================

st.title("🧠 My Second Brain")
st.caption("Asisten AI Lokal dengan RAG. Berjalan 100% Offline tanpa internet.")

# 2. Inisialisasi Database
@st.cache_resource
def load_database():
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    return client.get_collection(name="personal_kb", embedding_function=embed_fn)

try:
    collection = load_database()
except Exception as e:
    st.warning("Database belum tersedia. Silakan klik 'Hard Reset' di menu sebelah kiri.")
    st.stop()

# 3. Inisialisasi Memori Percakapan
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Kotak Input Pengguna
user_query = st.chat_input("Tanyakan sesuatu tentang catatanmu...")

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)

    results = collection.query(
        query_texts=[user_query],
        n_results=config.TOP_K
    )

    context_text = ""
    if results['documents'] and len(results['documents']) > 0 and len(results['documents'][0]) > 0:
        for i in range(len(results['documents'][0])):
            score = results['distances'][0][i]
            text = results['documents'][0][i]

            if score < 0.8:
                context_text += f"- {text}\n"

    # 5. Proses Berpikir AI
    if context_text == "":
        ai_answer = "Maaf, informasi tidak ditemukan di dalam catatan."
    else:
        system_instruction = f"""Anda adalah asisten AI Second Brain. Tugas satu-satunya Anda adalah mengekstrak informasi dari teks KONTEKS yang diberikan, bukan dari pengetahuan umum Anda.

Konteks dari database:
---
{context_text}
---

ATURAN WAJIB (JIKA DILANGGAR ANDA AKAN GAGAL):
1. Baca pertanyaan pengguna.
2. Cari jawabannya HANYA di dalam teks Konteks di atas.
3. JIKA Konteks di atas TIDAK MEMBAHAS atau TIDAK RELEVAN dengan pertanyaan pengguna (misalnya konteks membahas gulat, tapi pengguna bertanya tentang biologi/tokoh lain), Anda WAJIB menjawab dengan satu kalimat ini saja: "Maaf, informasi tidak ditemukan di dalam catatan."
4. DILARANG KERAS memberikan jawaban tebakan, mengarang fakta, atau melanjutkan cerita di luar apa yang tertulis di Konteks.
"""

        messages_to_send = [{'role': 'system', 'content': system_instruction}]
        messages_to_send.extend(st.session_state.chat_history)
        messages_to_send.append({'role': 'user', 'content': user_query})

        try:
            with st.spinner("AI sedang membaca catatan..."):
                response = ollama.chat(
                    model='gemma2:2b', 
                    messages=messages_to_send,
                    options={'temperature': 0.0}
                )
                ai_answer = response['message']['content']
        except Exception as e:
            ai_answer = f"Error Ollama: {e}"

    with st.chat_message("assistant"):
        st.markdown(ai_answer)

    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": ai_answer})

    if len(st.session_state.chat_history) > 6:
        st.session_state.chat_history = st.session_state.chat_history[-6:]