from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/api/sample-extract-pdf")
def sample_extract_pdf():
    """
    Sample API endpoint to demonstrate PDF content extraction and saving.
    This endpoint uses the save_pdf_content function from lib/pdf_extract to extract text from a PDF and save it to a file, which can then be used in a RAG chunking pipeline.
    """
    from lib.pdf import save_pdf_content
    
    pdf_path = "static/pdf/lexus_company_background.pdf"
    output_path = "output/lexus_company_background.txt"
    documents = save_pdf_content(pdf_path, output_path)
    
    # For demonstration, return the path to the saved text file
    return {"message": f"Successfully saved PDF content to {output_path}. (Timestamp: {datetime.now()})"}

@app.route("/api/sample-chunk-pdf")
def sample_chunk_pdf():
    """
    Sample API endpoint to demonstrate PDF content chunking and saving.
    This endpoint uses the chunk_text and save_chunks_to_json functions from lib/chunk to split a PDF's extracted text into chunks and save them to a JSON file.
    """
    from lib.chunk import chunk_text, save_chunks_to_json
    
    text_path = "output/lexus_company_background.txt"
    chunks = chunk_text(text_path, chunk_size=500, chunk_overlap=100)
    output_json_path = "output/lexus_company_background.json"
    save_chunks_to_json(chunks, output_json_path)
    
    # For demonstration, return the path to the saved JSON file
    return {"message": f"Successfully saved PDF chunks to {output_json_path}. (Timestamp: {datetime.now()})"}

@app.route("/api/sample-embed-text")
def sample_embed_text():
    """
    Reads a chunks JSON file, generates an embedding vector for each chunk's text,
    and saves a new JSON file with an 'embedding' field added to each chunk.
    """
    import json
    from lib.embed import embed_text

    input_path = "output/lexus_company_background.json"
    output_path = "output/lexus_company_background_embeddings.json"

    with open(input_path, "r") as f:
        data = json.load(f)

    chunks = data.get("chunks", [])
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["text"])

    output_data = {
        "total_chunks": len(chunks),
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimensions": 384,
        "chunks": chunks,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f)

    return {
        "message": f"Successfully embedded {len(chunks)} chunks and saved to {output_path}. (Timestamp: {datetime.now()})",
        "total_chunks": len(chunks),
        "output_file": output_path,
    }

@app.route("/api/sample-store-embeddings")
def sample_store_embeddings():
    """
    Reads a chunks JSON file with embeddings and stores them in a PostgreSQL database using the store_embeddings function from lib/vector.
    """
    import json
    from lib.vector import store_embeddings

    input_path = "output/lexus_company_background_embeddings.json"

    with open(input_path, "r") as f:
        data = json.load(f)

    chunks = data.get("chunks", [])
    num_inserted = store_embeddings(chunks)

    return {
        "message": f"Successfully stored {num_inserted} embedded chunks in the database. (Timestamp: {datetime.now()})",
        "total_chunks": num_inserted,
    }