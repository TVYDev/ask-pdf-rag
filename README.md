> 🚧 **Work in Progress** — This project is actively being developed and is not yet production-ready.

# ask-pdf-rag

A Flask API that extracts text from PDFs and prepares it for a Retrieval-Augmented Generation (RAG) pipeline by chunking and embedding the content into metadata-rich JSON.

---

## Pipeline Overview

```
PDF file
   │
   ▼
[1] Extract & save text          →  output/<name>.txt
        lib/pdf.py
        save_pdf_content()
   │
   ▼
[2] Chunk text by page           →  output/<name>.json
        lib/chunk.py
        chunk_text()
        save_chunks_to_json()
   │
   ▼
[3] Embed chunks                 →  output/<name>_embeddings.json
        lib/embed.py
        embed_text()
   │
   ▼
[4] Feed embeddings into RAG
    (vector store → retrieval → generation)
```

### Step 1 — PDF Extraction (`lib/pdf.py`)

`save_pdf_content(pdf_path, output_path)` loads a PDF with **PyMuPDF** via LangChain and writes a plain-text file where each page is prefixed with a header:

```
--- Page 0 | source: static/pdf/lexus_company_background.pdf ---
<page text>

--- Page 1 | source: static/pdf/lexus_company_background.pdf ---
<page text>
...
```

### Step 2 — Chunking (`lib/chunk.py`)

`chunk_text(text_path)` parses the page headers and splits each page's content using LangChain's `RecursiveCharacterTextSplitter` (default: 500 chars, 100 overlap). Every chunk retains its `page` number and `source` path.

`save_chunks_to_json(chunks, output_file)` persists those chunks to a JSON file ready for embedding ingestion.

### Step 3 — Embedding (`lib/embed.py`)

`embed_text(text)` converts a string into a 384-dimensional vector using **`sentence-transformers/all-MiniLM-L6-v2`** — a free, local model that runs entirely on-device with no API cost.

- The model is lazily loaded and cached as a module-level singleton (loaded once per process).
- Returns a `list[float]` ready to be stored in a vector database.
- Reads `HF_TOKEN` from `.env` via `python-dotenv` to suppress unauthenticated rate-limit warnings from the Hugging Face Hub.

```python
from lib.embed import embed_text

vector = embed_text("What is Lexus?")
print(len(vector))  # 384
```

---

## Project Structure

```
ask-pdf-rag/
├── app.py                  # Flask API endpoints
├── lib/
│   ├── pdf.py              # PDF loading & extraction
│   ├── chunk.py            # Text chunking & JSON export
│   └── embed.py            # Text → embedding vector
├── static/
│   └── pdf/
│       └── lexus_company_background.pdf
├── output/                 # Generated files (git-ignored)
│   ├── lexus_company_background.txt
│   ├── lexus_company_background.json
│   └── lexus_company_background_embeddings.json
├── .env                    # HF_TOKEN (git-ignored)
├── .gitignore
└── README.md
```

---

## Setup

```bash
# Clone & enter the project
git clone <repo-url> && cd ask-pdf-rag

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install flask langchain-community langchain-text-splitters pymupdf sentence-transformers python-dotenv

# Add your Hugging Face token to .env (get one free at https://huggingface.co/settings/tokens)
echo "HF_TOKEN=your_token_here" > .env
```

---

## Running the Server

```bash
flask --app app.py run
```

The server starts at `http://127.0.0.1:5000`.

---

## API Endpoints

### `GET /api/sample-extract-pdf`

Extracts text from `static/pdf/lexus_company_background.pdf` and saves it to `output/lexus_company_background.txt`.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-extract-pdf
```

**Response**

```json
{
  "message": "Successfully saved PDF content to output/lexus_company_background.txt. (Timestamp: 2026-03-03 12:00:00.123456)"
}
```

---

### `GET /api/sample-chunk-pdf`

Reads `output/lexus_company_background.txt`, splits it into chunks (500 chars / 100 overlap), and saves them to `output/lexus_company_background.json`.

> Run `/api/sample-extract-pdf` first to generate the source `.txt` file.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-chunk-pdf
```

**Response**

```json
{
  "message": "Successfully saved PDF chunks to output/lexus_company_background.json. (Timestamp: 2026-03-03 12:00:05.654321)"
}
```

**Output file — `output/lexus_company_background.json`**

```json
{
  "total_chunks": 42,
  "chunks": [
    {
      "index": 0,
      "page": 0,
      "source": "static/pdf/lexus_company_background.pdf",
      "text": "Lexus is the luxury vehicle division of Toyota..."
    },
    {
      "index": 1,
      "page": 0,
      "source": "static/pdf/lexus_company_background.pdf",
      "text": "Founded in 1989, Lexus has grown to become one of the best-selling luxury car brands..."
    }
  ]
}
```

---

### `GET /api/sample-embed-text`

Reads `output/lexus_company_background.json`, generates a **384-dimensional embedding vector** for each chunk using `sentence-transformers/all-MiniLM-L6-v2`, and saves the result to `output/lexus_company_background_embeddings.json`.

> Run `/api/sample-chunk-pdf` first to generate the chunks JSON file.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-embed-text
```

**Response**

```json
{
  "message": "Successfully embedded 42 chunks and saved to output/lexus_company_background_embeddings.json. (Timestamp: 2026-03-03 12:00:20.789123)",
  "total_chunks": 42,
  "output_file": "output/lexus_company_background_embeddings.json"
}
```

**Output file — `output/lexus_company_background_embeddings.json`**

```json
{
  "total_chunks": 42,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_dimensions": 384,
  "chunks": [
    {
      "index": 0,
      "page": 0,
      "source": "static/pdf/lexus_company_background.pdf",
      "text": "Lexus is the luxury vehicle division of Toyota...",
      "embedding": [0.0234, -0.1042, 0.0817, "...383 more values"]
    }
  ]
}
```

---

## Using the Library Directly

```python
from lib.pdf import save_pdf_content
from lib.chunk import chunk_text, save_chunks_to_json
from lib.embed import embed_text

# Step 1 — extract
save_pdf_content("static/pdf/lexus_company_background.pdf", "output/lexus_company_background.txt")

# Step 2 — chunk
chunks = chunk_text("output/lexus_company_background.txt", chunk_size=500, chunk_overlap=100)

# Step 3 — save chunks
save_chunks_to_json(chunks, "output/lexus_company_background.json")

# Step 4 — embed each chunk
for chunk in chunks:
    vector = embed_text(chunk["text"])  # list[float], 384 dims
    # store vector + chunk metadata in your vector DB
```

---

## Next Steps (RAG Pipeline)

1. ~~**Embed**~~ ✅ — `embed_text()` in `lib/embed.py` using `all-MiniLM-L6-v2`.
2. **Index** — store vectors + metadata (`page`, `source`) in a vector database (e.g. Chroma, Pinecone, pgvector).
3. **Retrieve** — on user query, embed the query and fetch the top-k relevant chunks.
4. **Generate** — pass retrieved context to an LLM to produce a grounded answer.
