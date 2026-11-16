import hashlib
import math
from typing import List, Optional, Any
from backend.app.core.config import settings


def generate_deterministic_embedding(text: str, dim: int = 768) -> List[float]:
    """
    Generate a normalized deterministic pseudo-embedding vector for offline/testing mode.
    Ensures identical texts have cosine similarity 1.0, and related keywords have high overlap.
    """
    words = text.lower().split()
    vector = [0.0] * dim
    
    for i, word in enumerate(words):
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vector[idx] += 1.0 + (1.0 / (i + 1))
        
        # Cross feature bucket
        idx2 = (h >> 4) % dim
        vector[idx2] += 0.5

    # Compute Euclidean norm
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    else:
        vector = [1.0 / math.sqrt(dim)] * dim
        
    return vector


class GeminiEmbedder:
    """Wrapper for text-embedding-004 using the google-genai SDK with fallback."""

    def __init__(self, gemini_client: Optional[Any] = None):
        self.client = gemini_client

    async def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        if not text or not text.strip():
            return [0.0] * 768

        if self.client and settings.has_gemini_key:
            try:
                response = await self.client.aio.models.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    contents=text
                )
                return response.embeddings[0].values
            except Exception as e:
                print(f"Warning: Gemini embedding failed: {e}. Using deterministic fallback.")

        return generate_deterministic_embedding(text, dim=768)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document strings."""
        if not texts:
            return []

        if self.client and settings.has_gemini_key:
            try:
                response = await self.client.aio.models.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    contents=texts
                )
                return [emb.values for emb in response.embeddings]
            except Exception as e:
                print(f"Warning: Gemini batch embeddings failed: {e}. Using deterministic fallback.")

        return [generate_deterministic_embedding(t, dim=768) for t in texts]
