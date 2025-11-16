"""Unit tests for embeddings."""

import pytest

from app.rag.embeddings import EmbeddingGenerator


def test_embedding_generator_initialization():
    """Test embedding generator initialization."""
    generator = EmbeddingGenerator()
    assert generator.model is not None


def test_generate_embedding():
    """Test generating a single embedding."""
    generator = EmbeddingGenerator()
    text = "def hello_world(): pass"
    embedding = generator.generate_embedding(text)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 embedding size
    assert all(isinstance(x, float) for x in embedding)


def test_generate_embeddings():
    """Test generating multiple embeddings."""
    generator = EmbeddingGenerator()
    texts = ["def hello(): pass", "def goodbye(): pass"]
    embeddings = generator.generate_embeddings(texts)
    assert len(embeddings) == 2
    assert all(len(e) == 384 for e in embeddings)

