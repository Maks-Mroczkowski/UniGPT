"""
RAG Retriever Module
Handles query-based retrieval from the vector store and LLM response generation
"""

from typing import Dict, Any, List
from vector_store import VectorStore
from embedding_manager import EmbeddingManager


class RAGRetriever:
    """Handles query-based retrieval from the vector store"""

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query

        Args:
            query: The query string
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score threshold

        Returns:
            List of retrieved documents with metadata and scores
        """
        print(f"Retrieving documents for query: {query}")

        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        # Search in vector store
        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            # Process results
            retrieved_docs = []

            if results['documents'] and results['documents'][0]:
                documents = results["documents"][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]

                for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):
                    similarity_score = 1 - distance

                    if similarity_score >= score_threshold:
                        retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i + 1
                        })

                print(f"Retrieved {len(retrieved_docs)} documents")
            else:
                print("No documents found")

            return retrieved_docs

        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []


def rag_simple(query: str, retriever: RAGRetriever, llm, top_k: int = 3) -> str:
    """
    Simple RAG function to answer queries

    Args:
        query: User's question
        retriever: RAGRetriever instance
        llm: Language model instance
        top_k: Number of relevant documents to retrieve

    Returns:
        Generated answer string
    """
    results = retriever.retrieve(query, top_k=top_k)
    context = '\n\n'.join([doc['content'] for doc in results]) if results else ""

    if not context:
        return "I don't have enough information to answer this question based on the lecture materials."

    prompt = f"""Use the following context from lecture materials to answer the question concisely.

Context: {context}

Question: {query}

Answer:"""

    response = llm.invoke(prompt)
    return response.content
