import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Matches headers written by save_pdf_content:
# --- Page 0 | source: path/to/file.pdf ---
_PAGE_HEADER_RE = re.compile(
    r"^--- Page (\d+) \| source: (.+?) ---$", re.MULTILINE
)


def chunk_text_content(text, chunk_size=500, chunk_overlap=100):
    """
    Chunk a raw string into smaller pieces with overlap.

    Args:
        text (str): The text content to chunk
        chunk_size (int): Maximum characters per chunk (default: 500)
        chunk_overlap (int): Overlap between consecutive chunks (default: 100)

    Returns:
        list[str]: List of text chunk strings

    Raises:
        Exception: For chunking errors
    """
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(text)
    except Exception as e:
        raise Exception(f"Error chunking text: {e}")


def chunk_text(text_path, chunk_size=500, chunk_overlap=100):
    """
    Chunk a saved PDF-extract file (produced by save_pdf_content) into pieces,
    preserving page number and source metadata on every chunk.

    The file is expected to contain page headers in the format:
        --- Page <n> | source: <path> ---

    Args:
        text_path (str): Path to the extracted text file
        chunk_size (int): Maximum characters per chunk (default: 500)
        chunk_overlap (int): Overlap between consecutive chunks (default: 100)

    Returns:
        list[dict]: Each item contains:
            - "text"   (str): The chunk text
            - "page"   (int): Source page number
            - "source" (str): Original PDF file path

    Raises:
        FileNotFoundError: If the text file doesn't exist
        Exception: For other chunking errors
    """
    if not os.path.exists(text_path):
        raise FileNotFoundError(f"Text file '{text_path}' not found.")

    try:
        with open(text_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # Split into (header_match, content) pairs
        matches = list(_PAGE_HEADER_RE.finditer(raw))

        if not matches:
            # Fallback: no page headers — treat entire file as one block
            return [{"text": chunk, "page": 0, "source": text_path}
                    for chunk in chunk_text_content(raw, chunk_size, chunk_overlap)]

        chunks = []
        for i, match in enumerate(matches):
            page_num = int(match.group(1))
            source = match.group(2).strip()

            # Content spans from end of this header to start of next (or EOF)
            content_start = match.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            page_text = raw[content_start:content_end].strip()

            for chunk in chunk_text_content(page_text, chunk_size, chunk_overlap):
                chunks.append({"text": chunk, "page": page_num, "source": source})

        return chunks

    except Exception as e:
        raise Exception(f"Error chunking text file: {e}")


def save_chunks_to_json(chunks, output_file):
    """
    Save the list of chunks produced by chunk_text to a JSON file.

    Args:
        chunks (list[dict]): Chunk list returned by chunk_text, where each item
                             contains "text", "page", and "source" keys.
        output_file (str): Path to the output JSON file.

    Returns:
        str: Absolute path to the saved JSON file.

    Raises:
        Exception: For I/O or serialisation errors.
    """
    import json

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        payload = {
            "total_chunks": len(chunks),
            "chunks": [
                {"index": i, "page": c["page"], "source": c["source"], "text": c["text"]}
                for i, c in enumerate(chunks)
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return os.path.abspath(output_file)

    except Exception as e:
        raise Exception(f"Error saving chunks to JSON: {e}")

