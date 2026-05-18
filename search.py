import chromadb
from chromadb.utils import embedding_functions
import config
import ollama

def main():
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    
    collection = client.get_collection(name=config.COLLECTION_NAME, embedding_function=embed_fn)

    print("==================================================")
    print("🧠 SECOND BRAIN AKTIF! (Ketik 'exit' untuk keluar)")
    print("==================================================")

    chat_history = []

    while True:
        user_query = input("\n> ")
        
        if user_query.lower() in ['exit', 'quit', 'keluar']:
            print("Mematikan Second Brain. Sampai jumpa!")
            break
        if not user_query.strip():
            continue

        results = collection.query(
            query_texts=[user_query],
            n_results=config.TOP_K,
            include=["documents", "distances", "metadatas"]
        )
        
        context_text = ""
        docs = []
        distances = []
        metas = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            print("\n🔍 [DEBUG] Hasil Tarikan Database:")
            docs = results['documents'][0]
            distances = results['distances'][0]
            metas = results['metadatas'][0] if results['metadatas'] else []

            for i in range(len(docs)):
                similarity_score = 1 - distances[i]
                score_percentage = similarity_score * 100
                source = metas[i].get('source', 'Unknown') if i < len(metas) else 'Unknown'
                
                print(f"   ➜ [Skor Relevansi: {score_percentage:.2f}%] Sumber: {source}")
                context_text += f"- [Sumber: {source}] \n{docs[i]}\n\n"

        if context_text == "":
            print("\nAI: Maaf, informasi tidak ditemukan di dalam catatan.")
            continue

        system_instruction = f"""Anda adalah asisten AI Second Brain yang cerdas.
Tugas Anda HANYA menjawab berdasarkan teks konteks yang diberikan di bawah ini.

ATURAN MUTLAK:
1. Jika jawaban TIDAK ADA di dalam teks konteks, Anda WAJIB menjawab persis seperti ini: "Maaf, informasi tersebut tidak ada di dalam catatan Anda."
2. JANGAN PERNAH mengarang informasi, menebak-nebak, atau mengambil ingatan dari luar teks konteks.
3. JANGAN menambahkan era, sejarah, atau fakta baru yang tidak tertulis di konteks.

Konteks:
{context_text}"""
        
        messages_to_send = [{'role': 'system', 'content': system_instruction}]
        messages_to_send.extend(chat_history)
        messages_to_send.append({'role': 'user', 'content': user_query})

        try:
            print("\nAI: ", end="", flush=True)
            
            response = ollama.chat(
                model='gemma2:2b', 
                messages=messages_to_send,
                options={'temperature': 0.0},
                stream=True 
            )
            
            ai_answer = ""
            for chunk in response:
                text_chunk = chunk['message']['content']
                print(text_chunk, end="", flush=True)
                ai_answer += text_chunk
            print() 

            if "maaf" in ai_answer.lower() and "tidak ada" in ai_answer.lower():
                if len(docs) > 0:
                    best_match_text = docs[0]
                    best_match_score = (1 - distances[0]) * 100
                    best_match_source = metas[0].get('source', 'Unknown')
                    
                    print(f"\n💡 [Saran Sistem]: Meskipun tidak ada jawaban spesifik untuk pertanyaan Anda, ini adalah catatan dengan topik terdekat yang saya temukan:")
                    print(f"   (Skor Relevansi: {best_match_score:.2f}% | Dokumen: {best_match_source})")
                    print(f"   \"{best_match_text.strip()}\"")

            chat_history.append({'role': 'user', 'content': user_query})
            chat_history.append({'role': 'assistant', 'content': ai_answer})

            if len(chat_history) > 6:
                chat_history = chat_history[-6:]
            
        except Exception as e:
            print(f"\nError Ollama: {e}")

if __name__ == "__main__":
    main()