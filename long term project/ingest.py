import os
import json
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2  # <-- Alat baru untuk membaca PDF
import config

def main():
    print("Memulai proses ingest data (Support Text & PDF)...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )

    collection = client.get_or_create_collection(
        name="personal_kb",
        embedding_function=embed_fn
    )

    processed_data = []
    chunk_id_counter = 1

    for category in config.CATEGORIES:
        folder_path = os.path.join(config.RAW_DIR, category)
        
        if not os.path.exists(folder_path):
            continue
            
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            text = "" # Variabel untuk menampung isi teks
            
            # 1. Jika filenya Markdown atau TXT
            if filename.endswith(".md") or filename.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
            # 2. Jika filenya PDF
            elif filename.endswith(".pdf"):
                print(f"Membaca file PDF: {filename}...")
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            extracted_text = page.extract_text()
                            if extracted_text:
                                text += extracted_text + "\n"
                except Exception as e:
                    print(f"Gagal membaca PDF {filename}: {e}")
                    continue
            else:
                continue # Abaikan file jenis lain (seperti gambar/audio)

            # Jika file kosong setelah dibaca, lewati
            text = text.strip()
            if not text:
                continue

            # Potong teks menjadi bagian kecil
            chunks = text_splitter.split_text(text)

            for chunk in chunks:
                metadata = {
                    "source": filename,
                    "category": category
                }
                
                chunk_id = f"chunk_{category}_{chunk_id_counter}"
                
                processed_data.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": metadata
                })
                
                chunk_id_counter += 1

    os.makedirs(os.path.dirname(config.PROCESSED_FILE), exist_ok=True)
    with open(config.PROCESSED_FILE, 'w', encoding='utf-8') as f:
        for item in processed_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"Berhasil memotong teks. Total {len(processed_data)} chunks disimpan.")

    if processed_data:
        ids = [item["id"] for item in processed_data]
        documents = [item["text"] for item in processed_data]
        metadatas = [item["metadata"] for item in processed_data]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print("Selesai! Semua catatan & PDF berhasil diserap ke dalam memori.")
    else:
        print("Tidak ada dokumen yang ditemukan untuk diproses.")

if __name__ == "__main__":
    main()