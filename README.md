> 🚧 **Work in Progress** — This project is actively being developed and is not yet production-ready.

# ask-pdf-rag

A Flask API that extracts text from PDFs and prepares it for a Retrieval-Augmented Generation (RAG) pipeline by chunking the content into metadata-rich JSON.

---

## Pipeline Overview

```
PDF file
   │
   ▼
[1] Extract & save text          →  output/<name>.txt
        lib/pdf_extract.py
        save_pdf_content()
   │
   ▼
[2] Chunk text by page           →  output/<name>_chunks.json
        lib/chunk.py
        chunk_text()
        save_chunks_to_json()
   │
   ▼
[3] Feed chunks into RAG
    (embeddings → vector store → retrieval)
```

### Step 1 — PDF Extraction (`lib/pdf.py`)

`save_pdf_content(pdf_path, output_path)` loads a PDF with **PyMuPDF** via LangChain and writes a plain-text file where each page is prefixed with a header:

```
--- Page 0 | source: static/pdf/swe_at_google.pdf ---
<page text>

--- Page 1 | source: static/pdf/swe_at_google.pdf ---
<page text>
...
```

### Step 2 — Chunking (`lib/chunk.py`)

`chunk_text(text_path)` parses the page headers and splits each page's content using LangChain's `RecursiveCharacterTextSplitter` (default: 500 chars, 100 overlap). Every chunk retains its `page` number and `source` path.

`save_chunks_to_json(chunks, output_file)` persists those chunks to a JSON file ready for embedding ingestion.

---

## Project Structure

```
ask-pdf-rag/
├── app.py                  # Flask API endpoints
├── lib/
│   ├── pdf.py              # PDF loading & extraction
│   └── chunk.py            # Text chunking & JSON export
├── static/
│   └── pdf/                # Place source PDF files here
├── output/                 # Generated .txt and .json files (git-ignored)
│   ├── swe_at_google.txt
│   └── swe_at_google_chunks.json
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
pip install flask langchain-community langchain-text-splitters pymupdf
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

Extracts text from `static/pdf/swe_at_google.pdf` and saves it to `output/swe_at_google.txt`.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-extract-pdf
```

**Response**

```json
{
  "message": "Successfully saved PDF content to output/swe_at_google.txt. (Timestamp: 2026-03-01 12:00:00.123456)"
}
```

---

### `GET /api/sample-chunk-pdf`

Reads `output/swe_at_google.txt`, splits it into chunks (500 chars / 100 overlap), and saves them to `output/swe_at_google_chunks.json`.

> Run `/api/sample-extract-pdf` first to generate the source `.txt` file.

**curl**

```bash
curl -X GET http://127.0.0.1:5000/api/sample-chunk-pdf
```

**Response**

```json
{
  "message": "Successfully saved PDF chunks to output/swe_at_google_chunks.json. (Timestamp: 2026-03-01 12:00:05.654321)"
}
```

**Output file — `output/swe_at_google_chunks.json`**

```json
{
  "total_chunks": 312,
  "chunks": [
    {
      "index": 0,
      "page": 0,
      "source": "static/pdf/swe_at_google.pdf",
      "text": "Software Engineering at Google\nLessons Learned from Programming Over Time\nEdited by Titus Winters, Tom Manshreck, and Hyrum Wright"
    },
    {
      "index": 1,
      "page": 0,
      "source": "static/pdf/swe_at_google.pdf",
      "text": "Programming is not Software Engineering. The addition of time, scale, and trade-offs adds a whole new dimension..."
    },
    {
      "index": 2,
      "page": 1,
      "source": "static/pdf/swe_at_google.pdf",
      "text": "Chapter 1: What Is Software Engineering?\nSoftware engineering is programming integrated over time..."
    }
  ]
}
```

---

## Using the Library Directly

```python
from lib.pdf import save_pdf_content
from lib.chunk import chunk_text, save_chunks_to_json

# Step 1 — extract
save_pdf_content("static/pdf/my_doc.pdf", "output/my_doc.txt")

# Step 2 — chunk
chunks = chunk_text("output/my_doc.txt", chunk_size=500, chunk_overlap=100)

# Step 3 — save for RAG ingestion
save_chunks_to_json(chunks, "output/my_doc_chunks.json")
```

---

## Next Steps (RAG Pipeline)

1. **Embed** — pass each `chunk["text"]` through an embedding model (e.g. OpenAI, Ollama).
2. **Index** — store vectors + metadata (`page`, `source`) in a vector database (e.g. Chroma, Pinecone, pgvector).
3. **Retrieve** — on user query, fetch the top-k relevant chunks.
4. **Generate** — pass retrieved context to an LLM to produce a grounded answer.
