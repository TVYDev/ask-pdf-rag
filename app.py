import json
import os
import uuid
from datetime import datetime

from flask import Flask, Response, render_template, request

from api import sample_bp

app = Flask(__name__)
app.register_blueprint(sample_bp)

UPLOAD_FOLDER = "output/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process-pdf", methods=["POST"])
def process_pdf():
    """
    Accepts a PDF upload and streams Server-Sent Events (SSE) reporting
    progress through the full RAG pipeline:
      1. Extract text  (lib/pdf.py)
      2. Chunk text    (lib/chunk.py)
      3. Embed chunks  (lib/embed.py)
      4. Store vectors (lib/vector.py)
    """
    if "pdf" not in request.files:
        return {"error": "No pdf file provided."}, 400

    pdf_file = request.files["pdf"]
    if not pdf_file.filename.lower().endswith(".pdf"):
        return {"error": "Only .pdf files are accepted."}, 400

    # Save the uploaded file with a unique name to avoid collisions
    safe_stem = os.path.splitext(pdf_file.filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    base_name = f"{safe_stem}_{unique_id}"

    pdf_path      = os.path.join(UPLOAD_FOLDER, f"{base_name}.pdf")
    txt_path      = os.path.join("output", f"{base_name}.txt")
    chunks_path   = os.path.join("output", f"{base_name}.json")
    embed_path    = os.path.join("output", f"{base_name}_embeddings.json")

    pdf_file.save(pdf_path)

    def event(type_, step=None, message="", **extra):
        payload = {"type": type_, "message": message}
        if step:
            payload["step"] = step
        payload.update(extra)
        return f"data: {json.dumps(payload)}\n\n"

    def generate():
        from lib.pdf import save_pdf_content
        from lib.chunk import chunk_text, save_chunks_to_json
        from lib.embed import embed_text
        from lib.vector import store_embeddings

        # ── Step 1: Extract ──────────────────────────────────────────────
        yield event("step_start", "extract", "Extracting text from PDF…")
        try:
            save_pdf_content(pdf_path, txt_path)
            yield event("step_done", "extract", "Text extracted successfully.")
        except Exception as e:
            yield event("step_error", "extract", str(e))
            return

        # ── Step 2: Chunk ────────────────────────────────────────────────
        yield event("step_start", "chunk", "Splitting text into chunks…")
        try:
            chunks = chunk_text(txt_path, chunk_size=500, chunk_overlap=100)
            save_chunks_to_json(chunks, chunks_path)
            yield event("step_done", "chunk", f"{len(chunks)} chunks created.")
        except Exception as e:
            yield event("step_error", "chunk", str(e))
            return

        # ── Step 3: Embed ────────────────────────────────────────────────
        yield event("step_start", "embed", "Generating embedding vectors…")
        try:
            for chunk in chunks:
                chunk["embedding"] = embed_text(chunk["text"])
            embed_data = {
                "total_chunks": len(chunks),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimensions": 384,
                "chunks": chunks,
            }
            with open(embed_path, "w") as f:
                json.dump(embed_data, f)
            yield event("step_done", "embed", f"{len(chunks)} vectors generated (384 dims).")
        except Exception as e:
            yield event("step_error", "embed", str(e))
            return

        # ── Step 4: Store ────────────────────────────────────────────────
        yield event("step_start", "store", "Inserting vectors into PostgreSQL…")
        try:
            rows = store_embeddings(chunks)
            yield event("step_done", "store", f"{rows} rows inserted into document_chunks.")
        except Exception as e:
            yield event("step_error", "store", str(e))
            return

        yield event("complete", message="Pipeline complete.",
                    total_chunks=len(chunks), rows_inserted=rows)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/ask", methods=["POST"])
def ask():
    """
    Embeds the user's query and returns the top-k most similar
    document chunks from the vector database.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return {"error": "No query provided."}, 400

    top_k = int(data.get("top_k", 5))

    from lib.embed import embed_text
    from lib.vector import search_similar

    query_vector = embed_text(query)
    results = search_similar(query_vector, top_k=top_k)

    return {"query": query, "results": results}