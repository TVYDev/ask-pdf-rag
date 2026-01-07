#!/usr/bin/env python3
"""
Text Chunker using LangChain
Splits text content into chunks with overlap.
"""

import sys
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text_content(text, chunk_size=500, chunk_overlap=100):
    """
    Chunk text content into smaller pieces with overlap.
    This function is designed to be imported and used in other modules.
    
    Args:
        text (str): The text content to chunk
        chunk_size (int): Maximum size of each chunk (default: 500 characters)
        chunk_overlap (int): Overlap between chunks (default: 100 characters)
    
    Returns:
        list: List of text chunks (strings)
    
    Raises:
        Exception: For chunking errors
    """
    try:
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        return chunks
    
    except Exception as e:
        raise Exception(f"Error chunking text: {e}")


def chunk_text(text_path, chunk_size=500, chunk_overlap=100):
    """
    Chunk text content from a file into smaller pieces with overlap.
    This function reads a file and chunks its content.
    
    Args:
        text_path (str): Path to the text file
        chunk_size (int): Maximum size of each chunk (default: 500 characters)
        chunk_overlap (int): Overlap between chunks (default: 100 characters)
    
    Returns:
        list: List of text chunks (strings)
    
    Raises:
        FileNotFoundError: If text file doesn't exist
        Exception: For other chunking errors
    """
    if not os.path.exists(text_path):
        raise FileNotFoundError(f"Text file '{text_path}' not found.")
    
    try:
        # Read text file
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Use the reusable function to chunk the text
        return chunk_text_content(text, chunk_size, chunk_overlap)
    
    except Exception as e:
        raise Exception(f"Error chunking text: {e}")



def main():
    """Main function to handle command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python chunk.py <text_file> [output_file] [chunk_size] [chunk_overlap]")
        print("Example: python chunk.py document.txt output.txt 500 100")
        print("\nDefault values:")
        print("  chunk_size: 500 characters (range: 200-500)")
        print("  chunk_overlap: 100 characters (range: 50-100)")
        sys.exit(1)
    
    text_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].isdigit() else None
    
    # Parse chunk_size and chunk_overlap
    if len(sys.argv) > 3:
        try:
            chunk_size = int(sys.argv[3] if not sys.argv[2].isdigit() else sys.argv[2])
        except ValueError:
            chunk_size = 500
    else:
        chunk_size = 500
    
    if len(sys.argv) > 4:
        try:
            chunk_overlap = int(sys.argv[4] if not sys.argv[2].isdigit() else sys.argv[3])
        except ValueError:
            chunk_overlap = 100
    else:
        chunk_overlap = 100
    
    # Validate ranges
    if not (200 <= chunk_size <= 500):
        print(f"Warning: chunk_size {chunk_size} is outside recommended range (200-500). Using anyway.")
    if not (50 <= chunk_overlap <= 100):
        print(f"Warning: chunk_overlap {chunk_overlap} is outside recommended range (50-100). Using anyway.")
    
    # Check if text file exists
    if not os.path.exists(text_path):
        print(f"Error: Text file '{text_path}' not found.")
        sys.exit(1)
    
    print(f"Processing: {text_path}\n")
    
    start_time = time.time()
    print(f"Starting chunking at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    
    try:
        # Chunk the text using the reusable function
        chunks = chunk_text(text_path, chunk_size, chunk_overlap)
        
        # Display chunk statistics
        total_chunks = len(chunks)
        print(f"Total chunks created: {total_chunks}")
        print(f"Chunk size: {chunk_size} characters")
        print(f"Chunk overlap: {chunk_overlap} characters\n")
        
        # Prepare output
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
        
        # Save or print the chunked text
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_output)
            print(f"Chunked text saved to: {output_path}")
        else:
            print(full_output)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nChunking completed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        print(f"Total time taken: {elapsed_time:.2f} seconds")
    
    except Exception as e:
        print(f"Error processing text file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
