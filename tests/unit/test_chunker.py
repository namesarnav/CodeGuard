"""Unit tests for code chunker."""

import pytest

from app.rag.chunker import CodeChunker


def test_chunker_initialization():
    """Test chunker initialization."""
    chunker = CodeChunker(chunk_size=500, chunk_overlap=100)
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 100


def test_chunk_python_file():
    """Test chunking a Python file."""
    chunker = CodeChunker()
    code = """
def hello_world():
    print("Hello, World!")

def goodbye_world():
    print("Goodbye, World!")
"""
    chunks = chunker.chunk_file(code, "test.py", "python")
    assert len(chunks) > 0
    assert all("content" in chunk for chunk in chunks)
    assert all("file_path" in chunk for chunk in chunks)
    assert all("language" in chunk for chunk in chunks)


def test_chunk_by_tokens():
    """Test chunking by token count."""
    chunker = CodeChunker(chunk_size=100, chunk_overlap=20)
    code = "\n".join([f"line {i}" for i in range(100)])
    chunks = chunker.chunk_file(code, "test.txt", "unknown")
    assert len(chunks) > 0

