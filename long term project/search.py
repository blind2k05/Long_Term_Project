import chromadb
from chromadb.utils import embedding_functions
import config
import ollama

def main():
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    collection = client.get_collection(name="personal_kb", embedding_function=embed_fn)

    print("SECOND BRAIN AKTIF! (Ketik 'exit' untuk keluar)")

    chat_history = []

    while True:
        user_query = input("\n> ")
        
        if user_query.lower() in ['exit', 'quit', 'keluar']:
            break
        if not user_query.strip():
            continue

        results = collection.query(
            query_texts=[user_query],
            n_results=config.TOP_K
        )

        context_text = ""
        for i in range(len(results['documents'][0])):
            score = results['distances'][0][i]
            text = results['documents'][0][i]

            if score < 0.8:
                context_text += f"- {text}\n"

        if context_text == "":
            print("AI: Maaf, informasi tidak ditemukan di dalam catatan.")
            continue

        system_instruction = f"""Kamu adalah asisten pribadi. Jawab HANYA berdasarkan konteks berikut:
        
Konteks:
{context_text}"""

        messages_to_send = [{'role': 'system', 'content': system_instruction}]
        messages_to_send.extend(chat_history)
        messages_to_send.append({'role': 'user', 'content': user_query})

        try:
            response = ollama.chat(
                model='gemma2:2b', 
                messages=messages_to_send,
                options={'temperature': 0.0}
            )
            ai_answer = response['message']['content']
            
            print(f"\nAI: {ai_answer}")

            chat_history.append({'role': 'user', 'content': user_query})
            chat_history.append({'role': 'assistant', 'content': ai_answer})

            if len(chat_history) > 6:
                chat_history = chat_history[-6:]
            
        except Exception as e:
            print(f"Error Ollama: {e}")

if __name__ == "__main__":
    main()