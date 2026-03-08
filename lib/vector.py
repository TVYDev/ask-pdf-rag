import psycopg2
from pgvector.psycopg2 import register_vector

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "rag_db",
    "user": "tvydev",
    "password": "tvydev",
}

_CREATE_EXTENSION = "CREATE EXTENSION IF NOT EXISTS vector;"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS document_chunks (
    id           SERIAL PRIMARY KEY,
    source       TEXT,
    page         INTEGER,
    chunk_index  INTEGER,
    text         TEXT,
    embedding    VECTOR(384)
);
"""


def _get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    return conn


def init_table():
    """Enable the pgvector extension and create document_chunks table if needed."""
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_EXTENSION)
            cur.execute(_CREATE_TABLE)
        conn.commit()


def store_embeddings(chunks: list[dict]) -> int:
    """Insert a list of embedded chunks into the document_chunks table.

    Each item in *chunks* must contain:
        - ``index``     (int)        : sequential chunk number
        - ``page``      (int)        : source page number
        - ``source``    (str)        : original PDF file path
        - ``text``      (str)        : chunk text
        - ``embedding`` (list[float]): 384-dimensional embedding vector

    Args:
        chunks: List of chunk dicts as produced by embed.py.

    Returns:
        Number of rows inserted.
    """
    if not chunks:
        return 0

    init_table()

    rows = [
        (
            chunk["source"],
            chunk["page"],
            chunk["index"],
            chunk["text"],
            chunk["embedding"],
        )
        for chunk in chunks
    ]

    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO document_chunks (source, page, chunk_index, text, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows,
            )
        conn.commit()

    return len(rows)
