import os
import json
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pymupdf4llm
import pandas as pd 
import config

def main(existing_collection=None):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    if existing_collection is not None:
        collection = existing_collection
    else:
        client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.EMBEDDING_MODEL_NAME
        )
        
        try:
            client.delete_collection(name=config.COLLECTION_NAME)
            print("Koleksi lama berhasil dihapus. Membangun ulang...")
        except Exception:
            print("Koleksi belum ada, membuat koleksi baru...")

        collection = client.create_collection(
            name=config.COLLECTION_NAME,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"}
        )

    processed_data = []

    for root, dirs, files in os.walk(config.RAW_DIR):
        category = os.path.basename(root)
        if category == "raw": 
            category = "General_Uploads"

        for filename in files:
            file_path = os.path.join(root, filename)
            text = ""
            
            if filename.endswith(".md") or filename.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
            elif filename.endswith(".pdf"):
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                except Exception as e:
                    print(f"Error mengekstrak PDF {filename}: {e}")
                    continue
            
            elif filename.endswith(".csv"):
                try:
                    df = pd.read_csv(file_path).astype(str)
                    csv_text = ""
                    for index, row in df.iterrows():
                        row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
                        csv_text += f"- {row_str}\n"
                    text += csv_text
                except Exception as e:
                    print(f"Error mengekstrak CSV {filename}: {e}")
                    continue
            else:
                continue

            text = text.strip()
            if not text:
                continue

            chunks = text_splitter.split_text(text)

            for index, chunk in enumerate(chunks):
                metadata = {
                    "source": filename,
                    "category": category
                }
                
                chunk_id = f"{filename}_chunk_{index + 1}"
                
                processed_data.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": metadata
                })

    if not processed_data:
        print("Tidak ada data untuk diproses.")
        return

    os.makedirs(os.path.dirname(config.PROCESSED_FILE), exist_ok=True)
    with open(config.PROCESSED_FILE, 'w', encoding='utf-8') as f:
        for item in processed_data:
            f.write(json.dumps(item) + '\n')

    ids = [item["id"] for item in processed_data]
    documents = [item["text"] for item in processed_data]
    metadatas = [item["metadata"] for item in processed_data]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print(f"Berhasil menelan {len(processed_data)} potongan teks ke dalam database.")

if __name__ == "__main__":
    main()