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
    
    pdf_path = "static/pdf/swe_at_google.pdf"
    output_path = "output/swe_at_google.txt"
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
    
    text_path = "output/swe_at_google.txt"
    chunks = chunk_text(text_path, chunk_size=500, chunk_overlap=100)
    output_json_path = "output/swe_at_google_chunks.json"
    save_chunks_to_json(chunks, output_json_path)
    
    # For demonstration, return the path to the saved JSON file
    return {"message": f"Successfully saved PDF chunks to {output_json_path}. (Timestamp: {datetime.now()})"}
