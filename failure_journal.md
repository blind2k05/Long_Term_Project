# Failure Journal & Bug Tracker

## Bug 1: AI Fails to Find Information (Model/Dimension Mismatch)
**Issue Explanation:**
When running the search system and asking about information that clearly exists in the notes, the terminal returns a failure message: *"AI: Sorry, information not found in the notes"*. This happens even though the relevant Markdown and PDF files are placed in the correct `raw` folder structure and the previous `ingest.py` process reported success.

**Root Cause Analysis:**
This issue arose after changing the `EMBEDDING_MODEL_NAME` variable in the configuration file to a new local/offline model. The existing ChromaDB database still stored the vector coordinates (number arrays) from the previous model. When the new model attempted to read or compare text with these old vectors, a *dimension mismatch* occurred, causing the search results to return zero text chunks.

**Fixed Treatment:**
1. **Database Hard Reset:** Manually deleted the `vault/chroma_db` folder and all its contents to remove residual vectors from the old model.
2. **Re-Ingestion Pipeline:** Re-ran `python ingest.py` from scratch so that all documents are re-converted into mathematical vectors using the new local embedding model.

---

## Bug 2: Database Locked & Ingest Failure via Web UI (Windows OS)
**Issue Explanation:**
After adding the Streamlit interface, the user attempted to re-ingest data using the button on the UI sidebar. However, the process failed, and the terminal/UI threw the error: *"PermissionError: [WinError 32] The process cannot access the file because it is being used by another process"*. Newly uploaded files were not ingested into the AI's memory.

**Root Cause Analysis:**
The Windows operating system utilizes a strict file protection mechanism (File Lock). While the Streamlit web app was running and "reading" the `chroma_db` folder, Windows locked the directory. Consequently, any Python commands (`shutil.rmtree` or data ingestion via background script) were denied by the OS.

**Fixed Treatment:**
1. **Force Cache Clearing:** Added the command `st.cache_resource.clear()` before initiating the ingestion or deletion process via the UI button. This forces Streamlit to "release" its grip on the database.
2. **Automated Hard Reset (UI Button):** Built a red "Hard Reset" button on the sidebar that clears the cache, deletes the `chroma_db` folder via `shutil`, and runs the ingestion function sequentially. (Note: If the lock persists, shut down the server via `Ctrl+C`, delete manually, and restart).

---

## Bug 3: Ingest Loader Fails to Read New Files (Directory Blindness)
**Issue Explanation:**
After uploading a new text file (`eksperimen_catboost.txt`) via Streamlit's Drag & Drop feature and running the ingest process, the total number of chunks reported in the terminal did not increase (it remained stuck at 17). The file was ignored as if it did not exist.

**Root Cause Analysis:**
The original `ingest.py` script utilized a static LangChain loader/loop configured to search for files **only within specific sub-folders** registered in `config.CATEGORIES` (e.g., `raw/journal/`). However, the Streamlit upload feature saves files directly in the root `raw/` folder. The ingest script was "blind" to any files located outside the predefined sub-folders.

**Fixed Treatment:**
**Refactoring Ingest Pipeline (os.walk):** Rewrote the search logic in `ingest.py` using the `os.walk(config.RAW_DIR)` function. This acts as a recursive scanner that automatically sweeps **all** files in the `raw` directory, including any current or future sub-folders, without needing manual registration.

---

## Bug 4: Relevant Documents Dropped by Strict Threshold Filter
**Issue Explanation:**
Even after a successful ingestion (chunk count increased to 19), the AI still replied with *"Sorry, information not found"*. This occurred despite the file containing the specific keyword being queried (e.g., CatBoost's depth parameter value).

**Root Cause Analysis:**
Inside the `search.py` (or `app.py`) script, there was a sorting rule: `if score < 0.8:`. Local embedding models often return proximity scores (L2 distance) slightly above 0.8 for sentences that are actually the correct answers (e.g., a score of 0.85). Consequently, highly relevant documents were being filtered out and dropped from the `context_text` variable before the LLM could even read them.

**Fixed Treatment:**
1. **Removal of Hard Limit:** Completely removed the `if score < 0.8` logic block. The system now allows the LLM to receive the `TOP_K` closest documents, regardless of the L2 score, letting the LLM's "brain" determine the actual relevance.
2. **Implementing X-Ray Feature (Context Debugger):** Added an `st.expander` named "Peek at the Documents Read by AI". This allows the user/developer to see exactly what text is pulled from the vector database before it is fed into the prompt, making future debugging much more measurable.

---

## Bug 5: Hallucinations and Context Loss Due to Improper Chunking (The NJPW Incident)
**Issue Explanation:**
When asking the AI to summarize the "Inoki Dark Ages" in NJPW based on a short journal entry, the AI either hallucinated by generating fictional facts (e.g., "unclear rule changes") or suddenly switched to answering in English, depending on how the text was ingested.

**Root Cause Analysis:**
The issue was traced to improper `CHUNK_SIZE` and `CHUNK_OVERLAP` settings in `config.py`. 
- When the chunk size was too small (e.g., 200 characters), the context was abruptly cut off, causing the small language model (Gemma 2B) to panic, lose its Indonesian language anchor, and revert to English.
- When using the older Multilingual embedding model with excessively large chunks (e.g., 1000 characters), the AI tried to "fill the gaps" in the short text, leading to creative hallucinations.

**Fixed Treatment:**
1. **Hyperparameter Tuning Script:** Created a dedicated `test_chunking.py` script using an Ephemeral (in-memory) ChromaDB client to run head-to-head comparisons of 9 different size and overlap combinations without corrupting the main database.
2. **Model Migration:** Replaced the older Multilingual embedding model with `BAAI/bge-m3`. The BGE-M3 model proved vastly superior at handling long contexts, allowing the `CHUNK_SIZE` to be safely increased to `1000` with an overlap of `50`. This combination resulted in highly accurate, hallucination-free summaries while preserving macro-level document structures.

## Bug 6: Streamlit App Crashes with "StreamlitDuplicateElementId"
**Issue Explanation:**
When running the updated UI, the Streamlit app suddenly crashed and displayed a red error box stating: *"There are multiple button/file_uploader elements with the same auto-generated ID"*. This prevented any interaction with the sidebar.

**Root Cause Analysis:**
Streamlit automatically generates internal IDs for widgets (like buttons or file uploaders) based on their text labels. If there are widgets with the same label, or if the UI re-renders dynamically and loses track of the elements, Streamlit gets confused and throws a duplication error.

**Fixed Treatment:**
**Explicit Key Assignment:** Modified `app.py` to pass a unique `key` argument to every interactive widget. For example: `st.button("🔄 Sinkronkan Data", key="btn_sync_data")` and `st.file_uploader(..., key="file_uploader_main")`. This acts as a definitive ID card for each element, completely resolving the crash.

---

## Bug 7: "module 'ingest' has no attribute 'main'" & Stale Server Memory
**Issue Explanation:**
After clicking the "Sinkronkan Data" button in the UI, an error appeared stating that the `ingest` module lacked a `main` attribute. Even after updating `ingest.py` with `def main():` and saving the file, the exact same error persisted in the Streamlit web app.

**Root Cause Analysis:**
This is a classic Python runtime and caching issue. While the physical `ingest.py` file was updated, the actively running Streamlit server and Python's `__pycache__` still held the older, outdated version of the script in memory. Python does not automatically hot-reload imported external modules.

**Fixed Treatment:**
1. **Script Refactoring:** Ensured `ingest.py` logic was properly encapsulated inside `def main(existing_collection=None):` with an `if __name__ == "__main__":` block.
2. **Hard Server Restart:** Shut down the Streamlit server in the terminal (`Ctrl+C`), optionally deleted the `__pycache__` folder to clear stale memory, and rebooted the server with `streamlit run app.py`.

---

## Bug 8: Tabular Data Failure & Context Noise (The "Sanity Filter" Dilemma)
**Issue Explanation:**
Two interrelated issues occurred: 
1. The small local LLM (Gemma 2B) failed to extract accurate information from uploaded CSV files (like network site data) because it couldn't natively execute Pandas queries.
2. When asking a short, specific question (e.g., "BTS capacity"), the AI sometimes pulled completely irrelevant documents (e.g., XGBoost notes) because the previous "Hard Limit Removal" (from Bug 4) forced ChromaDB to always return the `TOP_K` documents, regardless of how low the actual similarity was.

**Root Cause Analysis:**
Small parameter models (2B-8B) struggle with raw grid/tabular formats. Additionally, vector databases inherently operate on mathematical proximity; without a strict baseline threshold, the system will pull the "least wrong" document if the "right" document isn't perfectly matched, leading to context pollution.

**Fixed Treatment:**
1. **Row-to-Text Stringification:** Updated `ingest.py` to handle `.csv` files specifically. Instead of feeding raw grids, the script parses the dataframe and converts each row into a natural text string (e.g., `- site_id: xyz873 | rat: 4G LTE | status: Active`). This makes tabular data perfectly readable for small local LLMs.
2. **Re-introducing a Smarter "Sanity Filter":** Reverted the logic from Bug 4 by implementing a `MIN_SCORE = 0.45` threshold in `app.py`. Documents with a similarity score below 45% are now strictly dropped.
3. **Next Best Match (Fallback UI):** If all documents are dropped by the Sanity Filter (resulting in a blank context), the system instructs the LLM to explicitly say *"Sorry, information not found"*. However, the UI intelligently catches the highest-scoring dropped document and displays it as a *"System Suggestion"* to the user, balancing strict anti-hallucination rules with a helpful user experience.