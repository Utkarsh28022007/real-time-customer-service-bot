import os
import pytest
from backend.app.rag.ingest import chunk_markdown_file, load_all_knowledge_chunks
from backend.app.rag.embedder import generate_deterministic_embedding


def test_chunk_markdown_file():
    sample_file = "./data/knowledge_base/refunds_and_returns.md"
    if os.path.exists(sample_file):
        chunks = chunk_markdown_file(sample_file)
        assert len(chunks) > 0
        assert "metadata" in chunks[0]
        assert "source" in chunks[0]["metadata"]
        assert chunks[0]["metadata"]["source"] == "refunds_and_returns.md"


def test_load_all_knowledge_chunks():
    kb_dir = "./data/knowledge_base"
    chunks = load_all_knowledge_chunks(kb_dir)
    assert len(chunks) >= 5


def test_deterministic_embedding_properties():
    vec1 = generate_deterministic_embedding("How do I return my order?", dim=768)
    vec2 = generate_deterministic_embedding("How do I return my order?", dim=768)
    vec3 = generate_deterministic_embedding("Completely unrelated text about trees.", dim=768)

    assert len(vec1) == 768
    # Exact equality for identical input
    assert vec1 == vec2

    # Compute dot product (cosine similarity since vectors are unit length)
    similarity_same = sum(a * b for a, b in zip(vec1, vec2))
    assert abs(similarity_same - 1.0) < 1e-4

    similarity_diff = sum(a * b for a, b in zip(vec1, vec3))
    assert similarity_diff < 0.9
