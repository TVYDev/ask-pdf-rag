import sys
import os
import time
from langchain_community.document_loaders import PyMuPDFLoader

def load_pdf_documents(pdf_path):
    """
    Load PDF and return LangChain Document objects without printing or saving.
    This function is designed to be imported and used in other modules.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        list: List of LangChain Document objects (one per page)
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: For other PDF loading errors
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file '{pdf_path}' not found.")
    
    try:
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        return documents
    except Exception as e:
        raise Exception(f"Error loading PDF: {e}")


def read_pdf_content(pdf_path):
    """
    Read and return PDF content as a string without printing or saving.
    This function is designed to be imported and used in other modules.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text content from all pages

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: For other PDF loading errors
    """
    documents = load_pdf_documents(pdf_path)
    full_text = "".join(doc.page_content for doc in documents)
    return full_text


def save_pdf_content(pdf_path, output_file_path):
    """
    Extract text from a PDF and save it to a file for use in a RAG chunking pipeline.

    Each page is written with a separator comment so chunkers can respect page
    boundaries when splitting the document.

    Args:
        pdf_path (str): Path to the source PDF file
        output_file_path (str): Path where the extracted text file will be saved

    Returns:
        str: Absolute path to the saved output file

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: For other PDF loading or I/O errors
    """
    documents = load_pdf_documents(pdf_path)

    os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)

    with open(output_file_path, "w", encoding="utf-8") as f:
        for i, doc in enumerate(documents):
            page_num = doc.metadata.get("page", i)
            source = doc.metadata.get("source", pdf_path)
            f.write(f"--- Page {page_num} | source: {source} ---\n")
            f.write(doc.page_content)
            f.write("\n\n")

    return os.path.abspath(output_file_path)
