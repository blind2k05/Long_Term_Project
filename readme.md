# Second Brain: Hybrid RAG Assistant (Offline & Online)

## Explanation of the Project
This **Second Brain** project is an advanced Retrieval-Augmented Generation (RAG)-based AI assistant. The system is designed to read, remember, and answer questions based on personal notes, daily journals, PDF documents, and **Tabular Data (CSV)**. 

This project features a **Dual-Engine Architecture**:
1. **Privacy-Preserving Offline Mode:** Utilizes a local embedding model (`Sentence-Transformers`) and a local LLM (`Gemma 2B` via Ollama) for Zero-Cost Inference without sending any data to the internet.
2. **High-Performance Online Mode:** Connects to `Llama 3.1 8B` via the Groq API for lightning-fast reasoning and handling complex queries.

The system intelligently parses CSV files using a *Row-to-Text Stringification* technique, allowing small local models to answer tabular queries without needing to write or execute Python/Pandas code.

## Data Sources
Raw data is stored in the `vault/data/raw/` directory, which supports `.pdf`, `.md`, `.txt`, and `.csv` formats. My current knowledge base includes:
- **Journal entries:** Contains daily journals and personal interests, such as gaming updates and explorations of Japanese pro-wrestling history (e.g., NJPW Inoki Dark Ages).
- **School notes:** Contains lecture materials and paper drafts, such as notes on machine learning algorithms and university projects.
- **Internship & Operational Data:** Contains technical notes, RAG architecture documentation, and tabular `.csv` datasets (e.g., Telkomsel network site data and XGBoost churn prediction evaluation).

## Core Features (Streamlit Web UI)
This system comes with an interactive Graphical User Interface (UI) that runs directly in your browser.
- **Dual Model Toggle:** Switch seamlessly between Offline (Gemma 2B) and Online (Llama 3) models.
- **Multi-Format Upload:** Add PDF, TXT, MD, or CSV files directly from the sidebar. The system automatically ingests them into the vector space.
- **Relevancy Threshold (Sanity Filter):** The system strictly drops retrieved documents with a similarity score below **45%**, preventing AI hallucinations.
- **Next Best Match (Fallback):** If the answer is not found, the AI explicitly states it, but intelligently suggests the closest matching note available.
- **Document X-Ray (Peek):** A debugging feature to transparently see the exact text, source file, and similarity score the AI pulls from the database.
- **1-Click Database Management:** Sync or Hard Reset the ChromaDB vector database directly from the UI.

## Configuration
You can change the core settings of the search and text processing system in the `config.py` file:
- **`CHUNK_SIZE`**: Determines the maximum number of characters in a single text chunk.
- **`CHUNK_OVERLAP`**: Determines the number of overlapping characters between two consecutive text chunks to preserve context.
- **`TOP_K`**: Determines the number of top relevant reference documents to be extracted from ChromaDB.
- **`EMBEDDING_MODEL_NAME`**: Defines the embedding model used (default: `BAAI/bge-m3`).

---

## Troubleshooting & Manual Ingestion
The vector database synchronizes automatically via the Web UI. However, you can manually manage it via CLI. The `ingest.py` script acts as the data pipeline and ONLY needs to be executed manually if a massive batch of new files is added or if chunking parameters change.

**Error Solution: AI Fails to Find Context / Empty Results**
If you experience *vector collision* (differing matrix dimensions due to model or chunking changes), perform a **Hard Reset**:
1. Click the **"🔴 Hard Reset Database"** button in the Streamlit Sidebar.
2. Alternatively, manually delete the `vault/chroma_db/` folder and run `python ingest.py` in the terminal.

---

## 🚀 Quickstart Guide (Step-by-Step)

Follow these steps to run the Second Brain on your local machine:

**Step 1: System Requirements**
Ensure you have the following installed on your operating system:
* [Python 3.9+](https://www.python.org/downloads/)
* [Ollama](https://ollama.com/) (Required for Offline Mode)

**Step 2: Clone the Repository & Install Dependencies**
Open your terminal (or VS Code terminal) and run:
```bash
git clone <your-repository-url>
cd <your-repository-folder>
pip install -r requirements.txt
```
**Step 3: Setup the Local AI Brain (Gemma 2B)**
Download the offline language model into Ollama by running this command in your terminal:
```
ollama pull gemma2:2b
```

**Step 4: Setup the Online AI Brain (Groq API)** — OPTIONAL
(Set this up if you want to use the better/faster Llama 3 model)

Rename the env.example file to .env.
Open the .env file and insert your Groq API Key:

Code snippet
```
GROQ_API_KEY=your_actual_api_key_here
```
**Step 5: Run the Application**
Launch the Streamlit Web UI by executing:
```
streamlit run app.py
(If the command above is not recognized, use python -m streamlit run app.py)
```
**Step 6: Initialize the Database**
Upon first launch, the database will be empty.

Use the sidebar to upload your first document/CSV, OR

Click the "🔄 Sinkronkan Data (Update)" button to ingest existing files from the vault/data/raw/ folder.