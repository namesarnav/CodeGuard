"""Embedding generation for code chunks."""

from typing import List

from sentence_transformers import SentenceTransformer

from app.core.logging import get_logger

logger = get_logger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingGenerator:
    """Generate embeddings for code chunks."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        """
        Initialize embedding generator.

        Args:
            model_name: Name of the sentence transformer model
        """
        logger.info("Loading embedding model", model=model_name)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Embedding model loaded")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        logger.debug("Generating embeddings", count=len(texts))
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        embedding = self.model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()

