"""Qdrant vector store integration."""

import uuid
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VectorStore:
    """Qdrant vector store for code embeddings."""

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure collection exists, create if not."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            logger.info("Creating Qdrant collection", name=self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Collection created", name=self.collection_name)
        else:
            logger.debug("Collection exists", name=self.collection_name)

    def add_chunks(
        self,
        chunks: List[dict],
        embeddings: List[List[float]],
        scan_id: str,
    ) -> None:
        """
        Add code chunks with embeddings to vector store.

        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            scan_id: Scan identifier
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have same length")

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk["content"],
                        "file_path": chunk["file_path"],
                        "language": chunk["language"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                        "scan_id": scan_id,
                        **chunk.get("metadata", {}),
                    },
                )
            )

        logger.info("Adding points to vector store", count=len(points), scan_id=scan_id)
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info("Points added to vector store", count=len(points))

    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter_dict: Optional[dict] = None,
    ) -> List[dict]:
        """
        Search for similar code chunks.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filter_dict: Optional filter dictionary

        Returns:
            List of search results with scores
        """
        query_filter = None
        if filter_dict:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value),
                    )
                    for key, value in filter_dict.items()
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "score": result.score,
                "content": result.payload.get("content"),
                "file_path": result.payload.get("file_path"),
                "language": result.payload.get("language"),
                "start_line": result.payload.get("start_line"),
                "end_line": result.payload.get("end_line"),
                "metadata": {
                    k: v
                    for k, v in result.payload.items()
                    if k not in ["content", "file_path", "language", "start_line", "end_line"]
                },
            }
            for result in results
        ]

    def delete_scan_data(self, scan_id: str) -> None:
        """
        Delete all data for a specific scan.

        Args:
            scan_id: Scan identifier
        """
        logger.info("Deleting scan data from vector store", scan_id=scan_id)
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="scan_id",
                            match=models.MatchValue(value=scan_id),
                        )
                    ]
                )
            ),
        )
        logger.info("Scan data deleted", scan_id=scan_id)

