import os
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger("RAGPipeline")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class DocumentProcessor:
    """
    Handles text normalization, cleaning, and semantic chunking of ingested documents.
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalize and clean raw text, removing excessive spaces, bad formatting, 
        and non-printable characters.
        
        Args:
            text (str): Raw input text.
            
        Returns:
            str: Cleaned, normalized text.
        """
        if not text:
            return ""
        # Replace carriage returns with standard newlines
        text = re.sub(r'\r\n', '\n', text)
        # Replace multiple spaces with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Keep double newlines but clean empty lines in between
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    @staticmethod
    def semantic_chunk(text: str, max_words: int = 250, min_words: int = 40) -> List[str]:
        """
        Perform semantic chunking on the text. Groups text by natural boundaries 
        like double newlines (paragraphs), bullet lists, or section headings 
        rather than simple character/word limits.
        
        Args:
            text (str): Cleaned text body.
            max_words (int): Maximum words allowed per semantic chunk.
            min_words (int): Minimum words required to make a chunk (otherwise merged).
            
        Returns:
            List[str]: List of semantic chunks.
        """
        cleaned_text = DocumentProcessor.clean_text(text)
        if not cleaned_text:
            return []

        # Split by paragraph first
        paragraphs = cleaned_text.split('\n\n')
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_word_count = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_word_count = len(para.split())
            
            # If paragraph itself is excessively large, split it by sentence
            if para_word_count > max_words:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    sentence_word_count = len(sentence.split())
                    
                    if current_word_count + sentence_word_count > max_words:
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_word_count = sentence_word_count
                    else:
                        current_chunk.append(sentence)
                        current_word_count += sentence_word_count
            else:
                # Normal paragraph grouping
                if current_word_count + para_word_count > max_words:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    current_chunk = [para]
                    current_word_count = para_word_count
                else:
                    current_chunk.append(para)
                    current_word_count += para_word_count

        # Append last remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        # Optional: Merge very small ending chunks with the previous one
        final_chunks: List[str] = []
        for chunk in chunks:
            if not final_chunks:
                final_chunks.append(chunk)
            else:
                last_chunk_word_count = len(final_chunks[-1].split())
                current_chunk_word_count = len(chunk.split())
                
                if current_chunk_word_count < min_words and (last_chunk_word_count + current_chunk_word_count <= max_words):
                    final_chunks[-1] = final_chunks[-1] + "\n\n" + chunk
                else:
                    final_chunks.append(chunk)
                    
        return final_chunks


class EmbeddingEngine:
    """
    Encapsulates the SentenceTransformers embedding models.
    Operates independently of Granite models.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding model.
        """
        try:
            logger.info(f"Loading embedding model '{model_name}'...")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}", exc_info=True)
            raise e

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        """
        try:
            vector = self.model.encode(text, convert_to_numpy=True).tolist()
            return vector
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            raise e

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings in batch for a list of texts.
        """
        try:
            vectors = self.model.encode(texts, convert_to_numpy=True).tolist()
            return vectors
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}", exc_info=True)
            raise e


class VectorStore(ABC):
    """
    Abstract VectorStore to modularize database operations.
    Prevents business logic from directly binding to ChromaDB.
    """
    
    @abstractmethod
    def add_documents(self, collection_name: str, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        pass
        
    @abstractmethod
    def query(self, collection_name: str, query_text: str, n_results: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def clear_collection(self, collection_name: str) -> None:
        pass


class ChromaVectorStore(VectorStore):
    """
    ChromaDB implementation of the VectorStore interface.
    """
    
    def __init__(self, persist_path: str = "./chroma_db") -> None:
        """
        Initialize ChromaDB with persistence settings.
        """
        try:
            logger.info(f"Connecting to ChromaDB at '{persist_path}'...")
            self.client = chromadb.PersistentClient(path=persist_path)
            logger.info("ChromaDB persistent client successfully connected.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}", exc_info=True)
            raise e

    def _get_or_create_collection(self, collection_name: str):
        """
        Helper method to access a collection.
        """
        return self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, collection_name: str, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Add text documents and metadata to the specified collection.
        Embeddings are generated internally by Chroma if no embedding function is set,
        or handled through custom client calls.
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            logger.info(f"Adding {len(texts)} documents to collection '{collection_name}'...")
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info("Documents successfully inserted into ChromaDB.")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}", exc_info=True)
            raise e

    def query(self, collection_name: str, query_text: str, n_results: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query top K documents using cosine similarity/L2 from the specified collection.
        
        Returns:
            List[Dict[str, Any]]: List of matching documents and their metadata.
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            logger.info(f"Querying collection '{collection_name}' for '{query_text[:30]}...' (Top {n_results})")
            
            # Map simple filter query if exists
            where = filter_criteria if filter_criteria else None
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            formatted_results = []
            if results and 'documents' in results and results['documents']:
                docs = results['documents'][0]
                metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [None] * len(docs)
                ids = results['ids'][0]
                distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(docs)
                
                for idx in range(len(docs)):
                    formatted_results.append({
                        "id": ids[idx],
                        "document": docs[idx],
                        "metadata": metas[idx],
                        "distance": distances[idx]
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}", exc_info=True)
            return []

    def clear_collection(self, collection_name: str) -> None:
        """
        Resets and deletes all documents in a collection.
        """
        try:
            logger.info(f"Clearing collection '{collection_name}'...")
            self.client.delete_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' cleared successfully.")
        except Exception as e:
            logger.warning(f"Failed to clear collection '{collection_name}' (it may not exist): {str(e)}")
            pass


class RAGPipeline:
    """
    RAGPipeline orchestrates data ingestion, embedding, vector storage, and query retrieval.
    """
    
    def __init__(self, vector_store: VectorStore, embedding_engine: EmbeddingEngine) -> None:
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine

    def ingest_document(self, text: str, source_metadata: Dict[str, Any], collection_name: str = "kb_questions") -> None:
        """
        Ingest a document by cleaning it, spliting into semantic chunks, and storing in vector DB.
        
        Args:
            text (str): Full text of the document.
            source_metadata (Dict[str, Any]): Dict of meta details (difficulty, domain, source etc).
            collection_name (str): Collection name to write to.
        """
        chunks = DocumentProcessor.semantic_chunk(text)
        if not chunks:
            logger.warning("No valid chunks extracted from document.")
            return

        ids = [f"{source_metadata.get('source_id', 'doc')}_chunk_{i}" for i in range(len(chunks))]
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = source_metadata.copy()
            chunk_meta["chunk_index"] = i
            metadatas.append(chunk_meta)
            
        self.vector_store.add_documents(
            collection_name=collection_name,
            ids=ids,
            texts=chunks,
            metadatas=metadatas
        )
        logger.info(f"Ingested {len(chunks)} chunks into '{collection_name}'.")

    def retrieve_context(self, query: str, collection_name: str = "kb_questions", n_results: int = 3, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Retrieve context chunks from vector DB, formatting them into a unified string.
        
        Args:
            query (str): The search query.
            collection_name (str): Collection to search.
            n_results (int): Top K documents.
            filters (Optional[Dict[str, Any]]): Metadata filters.
            
        Returns:
            str: Context block for Granite prompts.
        """
        results = self.vector_store.query(
            collection_name=collection_name,
            query_text=query,
            n_results=n_results,
            filter_criteria=filters
        )
        
        if not results:
            return "No relevant context found."
            
        context_blocks = []
        for i, res in enumerate(results):
            meta = res["metadata"]
            source = meta.get("source", "Unknown Source")
            category = meta.get("category", "General")
            context_blocks.append(
                f"[Context Segment {i+1}] (Source: {source}, Category: {category})\n"
                f"{res['document']}"
            )
            
        return "\n\n".join(context_blocks)
