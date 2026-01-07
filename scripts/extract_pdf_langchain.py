#!/usr/bin/env python3
"""
PDF Content Extractor using LangChain
Extracts text content from PDF files using LangChain document loaders.
"""

import sys
import os
import time
from langchain_community.document_loaders import PyMuPDFLoader


def extract_text_from_pdf(pdf_path, output_path=None):
    """
    Extract text content from a PDF file using LangChain.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path to save extracted text. If None, prints to console.
    
    Returns:
        list: List of LangChain Document objects
    """
    start_time = time.time()
    print(f"Starting extraction at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    
    try:
        # Load PDF using LangChain's PyMuPDFLoader
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        
        # Display page count
        total_pages = len(documents)
        print(f"Total pages: {total_pages}\n")
        
        # Extract and combine text from all pages
        text_content = []
        for i, doc in enumerate(documents):
            page_num = doc.metadata.get('page', i)
            # text_content.append(f"--- Page {page_num + 1} ---\n{doc.page_content}\n")
            text_content.append(f"{doc.page_content}\n")
        
        # Combine all text
        # full_text = "\n".join(text_content)
        full_text = "".join(text_content)
        
        # Save or print the extracted text
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"Text extracted and saved to: {output_path}")
        else:
            print(full_text)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nExtraction completed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        print(f"Total time taken: {elapsed_time:.2f} seconds")
        
        return documents
    
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def extract_metadata(pdf_path):
    """
    Extract metadata from a PDF file using LangChain.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        dict: PDF metadata from first page
    """
    try:
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        if documents:
            return documents[0].metadata
        return None
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None


def main():
    """Main function to handle command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_langchain.py <pdf_file> [output_file]")
        print("Example: python extract_pdf_langchain.py document.pdf output.txt")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        sys.exit(1)
    
    # Extract and display metadata
    print(f"Processing: {pdf_path}\n")
    metadata = extract_metadata(pdf_path)
    if metadata:
        print("PDF Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        print()
    
    # Extract text content
    extract_text_from_pdf(pdf_path, output_path)


if __name__ == "__main__":
    main()
