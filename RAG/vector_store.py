"""
Vector Store Module
Manages document embeddings in a ChromaDB vector store
"""

import chromadb
import uuid
import os
import numpy as np
from typing import Dict, Any, List


class VectorStore:
    """Manages document embeddings in a ChromaDB vector store"""

    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "../Vector_store"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embeddings for RAG"}
            )
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")

        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[str], embeddings: np.ndarray, metadatas: List[Dict[str, Any]]) -> int:
        """Add documents to the vector store"""
        try:
            # Generate unique IDs for each document
            doc_ids = [f"doc_{uuid.uuid4()}_{i}" for i in range(len(documents))]

            # Add to collection
            self.collection.add(
                ids=doc_ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas
            )

            print(f"Added {len(documents)} documents to vector store")
            return len(documents)

        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise
