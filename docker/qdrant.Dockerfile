# Qdrant vector database
FROM qdrant/qdrant:latest

# Expose Qdrant ports
EXPOSE 6333 6334

# Qdrant will use default configuration
# Data will be persisted in /qdrant/storage volume

