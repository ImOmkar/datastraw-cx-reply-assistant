
import math

from google import genai
from google.genai import types

from backend.app.config import GEMINI_API_KEY, validate_ai_config


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

validate_ai_config()
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """Generate a normalized embedding for a policy or search query."""

    if not text or not text.strip():
        raise ValueError("Text must not be empty.")

    if task_type not in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}:
        raise ValueError(f"Unsupported embedding task type: {task_type}")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not response.embeddings or not response.embeddings[0].values:
        raise RuntimeError("Google returned an empty embedding.")

    embedding = [float(value) for value in response.embeddings[0].values]

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"received {len(embedding)}."
        )

    # Normalize the vector so cosine similarity is consistent.
    magnitude = math.sqrt(sum(value * value for value in embedding))

    if magnitude == 0:
        raise RuntimeError("Google returned a zero-magnitude embedding.")

    return [value / magnitude for value in embedding]
