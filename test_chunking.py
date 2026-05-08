import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
import config
import os

# ==========================================
# KONFIGURASI TES (SILAKAN UBAH BAGIAN INI)
# ==========================================
# 1. Pilih file yang sudah ada di folder raw Anda
FILE_TES = "vault/data/raw/journal/catatan_harian.md" 

# 2. Ubah pertanyaan agar relevan dengan isi file tersebut
PERTANYAAN = "jelaskan masa kelam njpw"

# 3. Parameter yang ingin diuji
chunk_sizes = [200, 500, 1000]
chunk_overlaps = [0, 50, 200]
# ==========================================

def main():
    if not os.path.exists(FILE_TES):
        print(f"❌ Error: File '{FILE_TES}' tidak ditemukan.")
        print("Silakan masukkan file yang benar atau buat file txt tersebut.")
        return

    # Baca isi file
    with open(FILE_TES, "r", encoding="utf-8") as f:
        text_content = f.read()

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        # model_name=config.EMBEDDING_MODEL_NAME
        model_name="BAAI/bge-m3"
    )

    print("==================================================")
    print("🧠 MEMULAI EKSPERIMEN CHUNKING RAG")
    print(f"📂 File: {FILE_TES}")
    print(f"❓ Pertanyaan: {PERTANYAAN}")
    print("==================================================\n")

    kombinasi_ke = 1

    # Looping semua kombinasi size dan overlap
    for size in chunk_sizes:
        for overlap in chunk_overlaps:
            
            print(f"\n--- [Tes {kombinasi_ke}/9] ---")
            kombinasi_ke += 1
            
            # Validasi Langchain: Overlap harus < Size
            if overlap >= size:
                print(f"⏩ SKIPPED: Size={size}, Overlap={overlap} (Overlap tidak boleh >= Size)")
                continue
                
            print(f"⚙️ Parameter: Chunk Size = {size} | Chunk Overlap = {overlap}")

            # 1. Potong teks sesuai kombinasi
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=size,
                chunk_overlap=overlap
            )
            chunks = splitter.split_text(text_content)
            
            print(f"📊 Dokumen terpotong menjadi {len(chunks)} bagian.")

            # 2. Buat Database Sementara (In-Memory, tidak mengganggu database asli)
            client = chromadb.EphemeralClient()
            collection = client.create_collection(
                name=f"test_{size}_{overlap}", 
                embedding_function=embed_fn,
                metadata={"hnsw:space": "cosine"}
            )

            # 3. Masukkan chunk ke database sementara
            collection.add(
                documents=chunks,
                ids=[f"id_{i}" for i in range(len(chunks))]
            )

            # 4. Cari dokumen teratas
            results = collection.query(
                query_texts=[PERTANYAAN],
                n_results=config.TOP_K
            )

            context_text = ""
            if results['documents'] and len(results['documents'][0]) > 0:
                for text in results['documents'][0]:
                    context_text += f"- {text}\n\n"

            # 5. Tanya AI
            system_instruction = f"""Kamu adalah asisten analitis. Jawab HANYA berdasarkan konteks berikut.
            
Konteks:
{context_text}"""

            messages_to_send = [
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': PERTANYAAN}
            ]

            try:
                response = ollama.chat(
                    model='gemma2:2b', 
                    messages=messages_to_send,
                    options={'temperature': 0.0}
                )
                ai_answer = response['message']['content']
                
                print(f"🤖 Jawaban AI:\n{ai_answer}")
                
            except Exception as e:
                print(f"❌ Error Ollama: {e}")

if __name__ == "__main__":
    main()