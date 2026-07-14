import logging
from typing import Dict, Any, Optional
from rag_pipeline import RAGPipeline, ChromaVectorStore, EmbeddingEngine

logger = logging.getLogger("RAGService")

class RAGService:
    """
    RAGService wraps the RAGPipeline and provides vector store and embedding operations 
    as a centralized service.
    """
    def __init__(self) -> None:
        try:
            logger.info("Initializing VectorStore and EmbeddingEngine for RAG Service...")
            self.vector_store = ChromaVectorStore()
            self.embedding_engine = EmbeddingEngine()
            self.pipeline = RAGPipeline(self.vector_store, self.embedding_engine)
            logger.info("RAG Service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {str(e)}", exc_info=True)
            raise e

    def ingest_document(self, text: str, source_metadata: Dict[str, Any], collection_name: str = "kb_questions") -> None:
        """
        Segment, clean, embed, and store a text document under the given metadata.
        """
        self.pipeline.ingest_document(text, source_metadata, collection_name)

    def retrieve_context(self, query: str, collection_name: str = "kb_questions", n_results: int = 3, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Query top-K relevant passages from vector store.
        """
        return self.pipeline.retrieve_context(query, collection_name, n_results, filters)
        
    def clear_collection(self, collection_name: str) -> None:
        """
        Deletes and resets a collection.
        """
        self.vector_store.clear_collection(collection_name)
