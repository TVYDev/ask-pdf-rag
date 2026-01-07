#!/usr/bin/env python3
"""
PDF Content Extractor using PyMuPDF
Extracts text content from PDF files.
"""

import fitz  # PyMuPDF
import sys
import os
import time


def read_pdf_content(pdf_path):
    """
    Read and return PDF content without printing or saving.
    This function is designed to be imported and used in other modules.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Extracted text content from all pages
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: For other PDF reading errors
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file '{pdf_path}' not found.")
    
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Extract text from all pages
        text_content = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content.append(text)
        
        # Close the document
        doc.close()
        
        # Combine all text
        full_text = "".join(text_content)
        return full_text
    
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")


def save_pdf_content(pdf_path, output_path):
    """
    Extract PDF content and save it to a text file.
    This function is designed to be imported and used in other modules.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str): Path to save the extracted text
    
    Returns:
        str: Path to the output file
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: For other PDF reading or writing errors
    """
    # Read PDF content
    content = read_pdf_content(pdf_path)
    
    # Save to output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path
    except Exception as e:
        raise Exception(f"Error saving content to file: {e}")


def extract_text_from_pdf(pdf_path, output_path=None):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path to save extracted text. If None, prints to console.
    
    Returns:
        str: Extracted text content
    """
    start_time = time.time()
    print(f"Starting extraction at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    
    try:
        # Open the PDF file to get page count
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        print(f"Total pages: {total_pages}\n")
        
        # Use the reusable function to read content
        full_text = read_pdf_content(pdf_path)
        
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
        
        return full_text
    
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def extract_metadata(pdf_path):
    """
    Extract metadata from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        dict: PDF metadata
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        return metadata
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None


def main():
    """Main function to handle command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file> [output_file]")
        print("Example: python extract_pdf.py document.pdf output.txt")
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
