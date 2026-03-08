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
[4] Store in vector database     →  PostgreSQL / pgvector
        lib/vector.py
        store_embeddings()
   │
   ▼
[5] Feed embeddings into RAG
    (retrieval → generation)
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

### Step 4 — Vector Storage (`lib/vector.py`)

`store_embeddings(chunks)` persists embedded chunks into a **PostgreSQL + pgvector** database.

- Calls `init_table()` internally, which enables the `vector` extension and creates the `document_chunks` table if they don't already exist.
- Accepts the same chunk list format produced by the embed step — each item must have `index`, `page`, `source`, `text`, and `embedding` fields.
- Uses `psycopg2` with the `pgvector` adapter for efficient `VECTOR(384)` inserts.
- Returns the number of rows inserted.

**Table schema — `document_chunks`**

| column        | type                 | description              |
| ------------- | -------------------- | ------------------------ |
| `id`          | `SERIAL PRIMARY KEY` | auto-increment row id    |
| `source`      | `TEXT`               | original PDF file path   |
| `page`        | `INTEGER`            | source page number       |
| `chunk_index` | `INTEGER`            | sequential chunk number  |
| `text`        | `TEXT`               | chunk text content       |
| `embedding`   | `VECTOR(384)`        | 384-dim embedding vector |

**Connection defaults**

| setting  | value       |
| -------- | ----------- |
| Host     | `localhost` |
| Port     | `5432`      |
| Database | `rag_db`    |
| Username | `tvydev`    |

```python
from lib.vector import store_embeddings
import json

with open("output/lexus_company_background_embeddings.json") as f:
    data = json.load(f)

inserted = store_embeddings(data["chunks"])
print(f"Inserted {inserted} rows")
```

---

## Project Structure

```
ask-pdf-rag/
├── app.py                  # Flask API endpoints
├── lib/
│   ├── pdf.py              # PDF loading & extraction
│   ├── chunk.py            # Text chunking & JSON export
│   ├── embed.py            # Text → embedding vector
│   └── vector.py           # Store embeddings in pgvector
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

## Technologies Required

### Language & Runtime

| Technology | Version | Purpose                                  |
| ---------- | ------- | ---------------------------------------- |
| **Python** | 3.10+   | Runtime language for the entire pipeline |

### Frameworks

| Technology    | Version | Purpose                  |
| ------------- | ------- | ------------------------ |
| **Flask**     | latest  | HTTP API server          |
| **LangChain** | latest  | Text splitting utilities |

### Libraries

| Technology                  | Version | Purpose                                    |
| --------------------------- | ------- | ------------------------------------------ |
| **PyMuPDF** (via LangChain) | latest  | PDF parsing and text extraction            |
| **sentence-transformers**   | latest  | Local embedding model (`all-MiniLM-L6-v2`) |
| **psycopg2-binary**         | latest  | Python PostgreSQL driver                   |
| **pgvector (Python)**       | latest  | psycopg2 adapter for the `VECTOR` type     |
| **python-dotenv**           | latest  | Load environment variables from `.env`     |

### Tools

| Technology | Version | Purpose                                                 |
| ---------- | ------- | ------------------------------------------------------- |
| **Docker** | latest  | Containerise and run the PostgreSQL + pgvector database |

### Databases & Extensions

| Technology     | Version | Purpose                                                          |
| -------------- | ------- | ---------------------------------------------------------------- |
| **PostgreSQL** | 16      | Relational database for vector storage                           |
| **pgvector**   | 0.7+    | PostgreSQL extension for the `VECTOR` type and similarity search |

### Platforms

| Technology       | Version | Purpose                                                                      |
| ---------------- | ------- | ---------------------------------------------------------------------------- |
| **Hugging Face** | —       | Model hub — hosts `all-MiniLM-L6-v2`; free account required for an API token |

---

## Setup

### 1. Clone the project

```bash
git clone <repo-url> && cd ask-pdf-rag
```

### 2. Start the PostgreSQL + pgvector database

Requires [Docker](https://docs.docker.com/get-docker/). The `pgvector/pgvector:pg16` image ships with the `vector` extension pre-installed.

```bash
docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=tvydev \
  -e POSTGRES_USER=tvydev \
  -e POSTGRES_DB=rag_db \
  -p 5432:5432 \
  -v pgvector_data:/var/lib/postgresql/data \
  pgvector/pgvector:pg16
```

Verify the container is running:

```bash
docker ps --filter name=pgvector-db
```

#### Enable the vector extension

Connect to the database and enable the extension once:

```bash
docker exec -it pgvector-db psql -U tvydev -d rag_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

> **Note:** `store_embeddings()` in `lib/vector.py` also runs this automatically on every call, so this step is optional but good practice to verify connectivity.

To stop / restart the container later:

```bash
docker stop pgvector-db
docker start pgvector-db
```

---

### 3. Set up Python environment

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install flask langchain-community langchain-text-splitters pymupdf sentence-transformers python-dotenv psycopg2-binary pgvector

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

### `GET /api/sample-store-embeddings`

Reads `output/lexus_company_background_embeddings.json` and inserts all embedded chunks into the `document_chunks` table in PostgreSQL using pgvector.

> Run `/api/sample-embed-text` first to generate the embeddings JSON file.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-store-embeddings
```

**Response**

```json
{
  "message": "Successfully stored 91 embedded chunks in the database. (Timestamp: 2026-03-08 12:00:30.123456)",
  "total_chunks": 91
}
```

---

## Using the Library Directly

```python
from lib.pdf import save_pdf_content
from lib.chunk import chunk_text, save_chunks_to_json
from lib.embed import embed_text
from lib.vector import store_embeddings

# Step 1 — extract
save_pdf_content("static/pdf/lexus_company_background.pdf", "output/lexus_company_background.txt")

# Step 2 — chunk
chunks = chunk_text("output/lexus_company_background.txt", chunk_size=500, chunk_overlap=100)

# Step 3 — save chunks
save_chunks_to_json(chunks, "output/lexus_company_background.json")

# Step 4 — embed each chunk
for chunk in chunks:
    chunk["embedding"] = embed_text(chunk["text"])  # list[float], 384 dims

# Step 5 — store in PostgreSQL / pgvector
inserted = store_embeddings(chunks)
print(f"Inserted {inserted} rows into document_chunks")
```

---

## Next Steps (RAG Pipeline)

1. ~~**Embed**~~ ✅ — `embed_text()` in `lib/embed.py` using `all-MiniLM-L6-v2`.
2. ~~**Index**~~ ✅ — `store_embeddings()` in `lib/vector.py` persists vectors + metadata into PostgreSQL via pgvector.
3. **Retrieve** — on user query, embed the query and fetch the top-k relevant chunks using a cosine/L2 similarity search against `document_chunks.embedding`.
4. **Generate** — pass retrieved context to an LLM to produce a grounded answer.
