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