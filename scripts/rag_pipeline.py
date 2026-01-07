#!/usr/bin/env python3
"""
PDF Processing Pipeline
Extract PDF content and chunk it into smaller pieces.
Uses reusable functions from extract_pdf.py and chunk.py
"""

import sys
import os
import time
import tempfile

# Add parent directory to path to import from scripts
sys.path.insert(0, os.path.dirname(__file__))

from extract_pdf import read_pdf_content
from chunk import chunk_text_content


def preprocess(pdf_path, chunk_size=500, chunk_overlap=100):
    """
    Preprocess PDF: extract content and chunk it.
    This function is designed to be imported and used in other modules.
    
    Args:
        pdf_path (str): Path to the PDF file
        chunk_size (int): Maximum size of each chunk (default: 500)
        chunk_overlap (int): Overlap between chunks (default: 100)
    
    Returns:
        list: List of text chunks (strings)
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: For other processing errors
    """
    # Read PDF content
    content = read_pdf_content(pdf_path)
    
    # Chunk the content
    chunks = chunk_text_content(content, chunk_size, chunk_overlap)
    
    return chunks


def process_pdf(input_path, output_path, chunk_size=500, chunk_overlap=100):
    """
    Process PDF: extract content and chunk it.
    
    Args:
        input_path (str): Path to input PDF file
        output_path (str): Path to output text file with chunks
        chunk_size (int): Maximum size of each chunk (default: 500)
        chunk_overlap (int): Overlap between chunks (default: 100)
    
    Returns:
        list: List of text chunks
    """
    start_time = time.time()
    print(f"Starting PDF processing at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}\n")
    
    try:
        # Use the reusable preprocess function to get chunks
        print("Step 1: Extracting PDF content...")
        print("Step 2: Chunking content...")
        chunks = preprocess(input_path, chunk_size, chunk_overlap)
        
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks")
        print(f"Chunk size: {chunk_size} characters")
        print(f"Chunk overlap: {chunk_overlap} characters\n")
        
        # Step 3: Save chunks to output file
        print("Step 3: Saving chunks to output file...")
        output_lines = []
        for i, chunk in enumerate(chunks):
            chunk_header = f"=== Chunk {i + 1}/{total_chunks} ==="
            chunk_length = f"Length: {len(chunk)} characters"
            
            output_lines.append(chunk_header)
            output_lines.append(chunk_length)
            output_lines.append("-" * 50)
            output_lines.append(chunk)
            output_lines.append("\n")
        
        full_output = "\n".join(output_lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_output)
        
        print(f"Chunks saved to: {output_path}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nProcessing completed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        print(f"Total time taken: {elapsed_time:.2f} seconds")
        
        return chunks
    
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None


def main():
    """Main function to handle command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python rag_pipeline.py <input_pdf> [output_file] [chunk_size] [chunk_overlap]")
        print("Example: python rag_pipeline.py input.pdf output.txt 500 100")
        print("Example: python rag_pipeline.py input.pdf  (uses default output directory)")
        print("\nDefault values:")
        print("  output_file: output/chunks_<epoch_time>.txt")
        print("  chunk_size: 500 characters")
        print("  chunk_overlap: 100 characters")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Check if input PDF exists
    if not os.path.exists(input_path):
        print(f"Error: Input PDF file '{input_path}' not found.")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) > 2 and not sys.argv[2].isdigit():
        output_path = sys.argv[2]
        chunk_size = int(sys.argv[3]) if len(sys.argv) > 3 else 500
        chunk_overlap = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    else:
        # Use default output directory with epoch time
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        epoch_time = int(time.time())
        output_path = os.path.join(output_dir, f'chunks_{epoch_time}.txt')
        
        chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
        chunk_overlap = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    # Process the PDF
    process_pdf(input_path, output_path, chunk_size, chunk_overlap)


if __name__ == "__main__":
    main()
