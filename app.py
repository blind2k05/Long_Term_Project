import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import config
import ollama
import os
import subprocess
import shutil
from groq import Groq
import ingest

os.makedirs(os.path.join("vault", "data", "raw"), exist_ok=True)

st.set_page_config(page_title="Second Brain AI", page_icon="🧠", layout="centered")

@st.cache_resource
def load_database():
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    return client.get_collection(name=config.COLLECTION_NAME, embedding_function=embed_fn)

try:
    collection = load_database()
except Exception as e:
    st.warning("Database belum tersedia. Lakukan Hard Reset.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Pengaturan Mesin AI")
    llm_mode = st.radio(
        "Pilih Mode Operasi:",
        ["🔒 Offline (Ollama - Gemma 2B)", "☁️ Online (Groq - Llama 3)"]
    )
    st.divider()
    
    st.header("📂 Tambah Catatan Baru")
    uploaded_file = st.file_uploader("Pilih file PDF, TXT, MD, atau CSV", type=["pdf", "txt", "md", "csv"], key="file_uploader_main")
    if uploaded_file is not None:
        save_path = os.path.join("vault", "data", "raw", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Menyerap dokumen baru otomatis..."):
            try:
                ingest.main(existing_collection=collection) 
                st.success(f"✅ '{uploaded_file.name}' terserap ke memori!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.header("🛠️ Manajemen Database")
    
    if st.button("🔄 Sinkronkan Data (Update)", key="btn_sync_data"):
        with st.spinner("Membaca perubahan file terbaru..."):
            try:
                ingest.main(existing_collection=collection)
                st.success("Memori berhasil diperbarui!")
            except Exception as e:
                st.error(f"Gagal sinkronisasi: {e}")
    
    if st.button("🔴 Hard Reset Database", key="btn_hard_reset"):
        with st.spinner("Meremove dan rebuild database..."):
            try:
                st.cache_resource.clear()
                if os.path.exists(config.CHROMA_PATH):
                    shutil.rmtree(config.CHROMA_PATH, ignore_errors=True)
                subprocess.run(["python", "ingest.py"], check=True)
                st.success("Hard Reset Berhasil!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal reset: {e}")

    st.divider()
    if st.button("🗑️ Hapus Obrolan", key="btn_clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

st.title("🧠 My Second Brain")
st.caption("Asisten AI Cerdas dengan dukungan Hybrid RAG (Offline/Online).")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Tanyakan sesuatu...")

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)

    results = collection.query(
        query_texts=[user_query],
        n_results=config.TOP_K,
        include=["documents", "distances", "metadatas"]
    )

    context_text = ""
    unique_sources = set()
    display_context_ui = "" 
    
    docs = []
    distances = []
    metas = []

    if results['documents'] and len(results['documents'][0]) > 0:
        raw_docs = results['documents'][0]
        raw_distances = results['distances'][0]
        raw_metas = results['metadatas'][0] if results['metadatas'] else []

        for i in range(len(raw_docs)):
            similarity_score = 1 - raw_distances[i]
            if similarity_score >= config.MIN_SCORE:
                docs.append(raw_docs[i])
                distances.append(raw_distances[i])
                metas.append(raw_metas[i])

    for i in range(len(docs)):
        source = metas[i].get('source', 'Tidak diketahui') if i < len(metas) else 'Tidak diketahui'
        category = metas[i].get('category', 'Umum') if i < len(metas) else 'Umum'
        unique_sources.add(source)
        
        score_percentage = (1 - distances[i]) * 100
        
        context_text += f"- [Sumber: {source}]\n{docs[i]}\n\n"
        display_context_ui += f"**Dokumen {i+1}** (Skor: `{score_percentage:.2f}%` | Folder: `{category}` | File: `{source}`)\n> {docs[i]}\n\n---\n"

    with st.expander("🔍 Intip Dokumen & Skor Relevansi"):
        st.markdown(display_context_ui if display_context_ui else "Tidak ada dokumen yang memenuhi batas relevansi (>45%).")

    if context_text == "":
        with st.chat_message("assistant"):
            st.markdown("Maaf, informasi tidak ditemukan di catatan.")
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": "Maaf, informasi tidak ditemukan di catatan."})
    else:
        system_instruction = f"""Anda adalah asisten AI pengekstraksi fakta. 
Tugas Anda HANYA menyampaikan informasi dari "Konteks Catatan" di bawah ini.

Konteks Catatan:
---
{context_text}
---

ATURAN MUTLAK (WAJIB DIPATUHI):
1. LANGSUNG KE INTI: Dilarang keras berbasa-basi, menyapa, atau menggunakan frasa seperti "Wah seru banget" atau "Mari kita bahas".
2. HILANGKAN KATA GANTI CATATAN: Jangan pernah berkata "Menurut catatan...", "Berdasarkan dokumen...", atau "Pengguna tertarik...". Langsung sampaikan faktanya seolah itu adalah jawaban mutlak.
3. ANTI-HALUSINASI: Dilarang menambahkan fakta, sejarah, nama tokoh, atau nama perusahaan dari luar Konteks Catatan.
4. JAWABAN KOSONG: Jika Konteks Catatan tidak membahas pertanyaan, Anda HANYA BOLEH menjawab persis dengan kalimat ini: "Maaf, informasi tersebut tidak ada di dalam catatan." Dilarang menambah kalimat apa pun setelahnya.
"""

        messages_to_send = [{'role': 'system', 'content': system_instruction}]
        messages_to_send.extend(st.session_state.chat_history)
        messages_to_send.append({'role': 'user', 'content': user_query})

        with st.chat_message("assistant"):
            try:
                if "Offline" in llm_mode:
                    def stream_ollama():
                        response = ollama.chat(
                            model=config.OFFLINE_LLM_MODEL, 
                            messages=messages_to_send,
                            options={'temperature': 0.0},
                            stream=True
                        )
                        for chunk in response:
                            yield chunk['message']['content']
                    
                    full_response = st.write_stream(stream_ollama)

                else:
                    if not config.GROQ_API_KEY:
                        full_response = st.markdown("Error: API Key Groq tidak ditemukan di .env.")
                    else:
                        client = Groq(api_key=config.GROQ_API_KEY)
                        def stream_groq():
                            chat_completion = client.chat.completions.create(
                                messages=messages_to_send,
                                model=config.ONLINE_LLM_MODEL, 
                                temperature=0.0,
                                stream=True
                            )
                            for chunk in chat_completion:
                                if chunk.choices[0].delta.content is not None:
                                    yield chunk.choices[0].delta.content
                                    
                        full_response = st.write_stream(stream_groq)
                
                fallback_ui = ""
                if "maaf" in full_response.lower() and "tidak ada" in full_response.lower():
                    if len(docs) > 0:
                        best_match_text = docs[0]
                        best_match_score = (1 - distances[0]) * 100
                        best_match_source = metas[0].get('source', 'Unknown')
                        
                        fallback_ui = f"\n\n💡 **Saran Sistem:** Meskipun tidak ada jawaban spesifik, ini adalah catatan terdekat yang ditemukan (Skor: `{best_match_score:.2f}%` dari `{best_match_source}`):\n> *\"{best_match_text.strip()}\"*"
                        st.markdown(fallback_ui)

                sources_str = f"\n\n---\n**📄 Referensi:** {', '.join(unique_sources)}"
                st.markdown(sources_str)
                
                final_answer_to_save = full_response + fallback_ui + sources_str

            except Exception as e:
                st.error(f"Error: {e}")
                final_answer_to_save = f"Error: {e}"

        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": final_answer_to_save})

        if len(st.session_state.chat_history) > 6:
            st.session_state.chat_history = st.session_state.chat_history[-6:]