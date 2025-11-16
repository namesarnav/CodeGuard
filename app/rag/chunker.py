"""Code chunking for RAG."""

import re
from typing import List

import tiktoken

from app.core.logging import get_logger

logger = get_logger(__name__)

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


class CodeChunker:
    """Chunk code files for embedding."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> None:
        """
        Initialize code chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Failed to load tiktoken encoding, using fallback")
            self.encoding = None

    def chunk_file(
        self,
        content: str,
        file_path: str,
        language: str,
        metadata: dict | None = None,
    ) -> List[dict]:
        """
        Chunk a code file into smaller pieces.

        Args:
            content: File content
            file_path: File path
            language: Programming language
            metadata: Additional metadata

        Returns:
            List of chunk dictionaries
        """
        if metadata is None:
            metadata = {}

        # Try to chunk by functions/classes first for better context
        if language in ["python", "javascript", "typescript", "java", "go", "rust"]:
            chunks = self._chunk_by_structure(content, file_path, language, metadata)
        else:
            chunks = self._chunk_by_tokens(content, file_path, language, metadata)

        logger.debug(
            "Chunked file",
            file_path=file_path,
            language=language,
            chunks=len(chunks),
        )
        return chunks

    def _chunk_by_structure(
        self,
        content: str,
        file_path: str,
        language: str,
        metadata: dict,
    ) -> List[dict]:
        """Chunk code by functions/classes when possible."""
        lines = content.split("\n")
        chunks = []
        current_chunk_lines = []
        current_tokens = 0
        current_start_line = 1

        for i, line in enumerate(lines, start=1):
            line_tokens = self._count_tokens(line)

            # Check if adding this line would exceed chunk size
            if current_tokens + line_tokens > self.chunk_size and current_chunk_lines:
                # Save current chunk
                chunk_content = "\n".join(current_chunk_lines)
                chunks.append(
                    {
                        "content": chunk_content,
                        "file_path": file_path,
                        "language": language,
                        "start_line": current_start_line,
                        "end_line": i - 1,
                        "metadata": {
                            **metadata,
                            "chunk_index": len(chunks),
                        },
                    }
                )

                # Start new chunk with overlap
                overlap_lines = self._get_overlap_lines(
                    current_chunk_lines, self.chunk_overlap
                )
                current_chunk_lines = overlap_lines + [line]
                current_tokens = sum(self._count_tokens(l) for l in current_chunk_lines)
                current_start_line = i - len(overlap_lines)
            else:
                current_chunk_lines.append(line)
                current_tokens += line_tokens

        # Add final chunk
        if current_chunk_lines:
            chunk_content = "\n".join(current_chunk_lines)
            chunks.append(
                {
                    "content": chunk_content,
                    "file_path": file_path,
                    "language": language,
                    "start_line": current_start_line,
                    "end_line": len(lines),
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                    },
                }
            )

        return chunks

    def _chunk_by_tokens(
        self,
        content: str,
        file_path: str,
        language: str,
        metadata: dict,
    ) -> List[dict]:
        """Chunk content by token count."""
        lines = content.split("\n")
        chunks = []
        current_chunk_lines = []
        current_tokens = 0
        current_start_line = 1

        for i, line in enumerate(lines, start=1):
            line_tokens = self._count_tokens(line)

            if current_tokens + line_tokens > self.chunk_size and current_chunk_lines:
                chunk_content = "\n".join(current_chunk_lines)
                chunks.append(
                    {
                        "content": chunk_content,
                        "file_path": file_path,
                        "language": language,
                        "start_line": current_start_line,
                        "end_line": i - 1,
                        "metadata": {
                            **metadata,
                            "chunk_index": len(chunks),
                        },
                    }
                )

                # Overlap
                overlap_lines = self._get_overlap_lines(
                    current_chunk_lines, self.chunk_overlap
                )
                current_chunk_lines = overlap_lines + [line]
                current_tokens = sum(self._count_tokens(l) for l in current_chunk_lines)
                current_start_line = i - len(overlap_lines)
            else:
                current_chunk_lines.append(line)
                current_tokens += line_tokens

        if current_chunk_lines:
            chunk_content = "\n".join(current_chunk_lines)
            chunks.append(
                {
                    "content": chunk_content,
                    "file_path": file_path,
                    "language": language,
                    "start_line": current_start_line,
                    "end_line": len(lines),
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                    },
                }
            )

        return chunks

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.encoding:
            return len(self.encoding.encode(text))
        # Fallback: approximate 1 token = 4 characters
        return len(text) // 4

    def _get_overlap_lines(self, lines: List[str], overlap_tokens: int) -> List[str]:
        """Get overlap lines from the end of current chunk."""
        overlap_lines = []
        tokens = 0

        for line in reversed(lines):
            line_tokens = self._count_tokens(line)
            if tokens + line_tokens > overlap_tokens:
                break
            overlap_lines.insert(0, line)
            tokens += line_tokens

        return overlap_lines

    def extract_function_name(self, content: str, language: str) -> str | None:
        """Extract function name from code chunk."""
        patterns = {
            "python": r"def\s+(\w+)\s*\(",
            "javascript": r"function\s+(\w+)\s*\(",
            "typescript": r"(?:function\s+)?(\w+)\s*[=:]\s*(?:\([^)]*\)\s*)?=>",
            "java": r"(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(",
            "go": r"func\s+(\w+)\s*\(",
            "rust": r"fn\s+(\w+)\s*\(",
        }

        pattern = patterns.get(language)
        if pattern:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None

