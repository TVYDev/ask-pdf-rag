import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed_text(text: str) -> list[float]:
    """Embed a string of text using sentence-transformers/all-MiniLM-L6-v2.

    Args:
        text: The input string to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
