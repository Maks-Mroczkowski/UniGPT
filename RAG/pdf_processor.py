"""
PDF Processor Module
Handles PDF loading, chunking, and embedding generation
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Tuple
from embedding_manager import EmbeddingManager
from vector_store import VectorStore


def process_pdf(
    filepath: str,
    original_filename: str,
    embedding_manager: EmbeddingManager,
    vectorstore: VectorStore
) -> Tuple[int, int]:
    """
    Process a PDF file: load, chunk, embed, and add to vector store

    Args:
        filepath: Path to the PDF file
        original_filename: Original name of the file
        embedding_manager: EmbeddingManager instance
        vectorstore: VectorStore instance

    Returns:
        Tuple of (num_pages, num_chunks)
    """
    print(f"Processing PDF: {original_filename}")

    # Load PDF
    loader = PyPDFLoader(filepath)
    documents = loader.load()
    num_pages = len(documents)
    print(f"Loaded {num_pages} pages from {original_filename}")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    num_chunks = len(chunks)
    print(f"Split into {num_chunks} chunks")

    # Extract text and metadata
    texts = [chunk.page_content for chunk in chunks]
    metadatas = []

    for i, chunk in enumerate(chunks):
        metadata = chunk.metadata.copy()
        metadata['source_file'] = original_filename
        metadata['file_type'] = 'pdf'
        metadata['content_length'] = len(chunk.page_content)
        metadata['doc_index'] = i
        metadatas.append(metadata)

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = embedding_manager.generate_embeddings(texts)
    print(f"Generated {len(embeddings)} embeddings")

    # Add to vector store
    print("Adding to vector store...")
    vectorstore.add_documents(texts, embeddings, metadatas)
    print(f"Successfully added {num_chunks} chunks to vector store")

    return num_pages, num_chunks
