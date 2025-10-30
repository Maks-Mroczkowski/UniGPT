"""
UniGPT Main Module
Demonstrates usage of the modularized RAG components
Can be used for testing or as a standalone script
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Import custom modules
from embedding_manager import EmbeddingManager
from vector_store import VectorStore
from rag_retriever import RAGRetriever, rag_simple
from pdf_processor import process_pdf
from upload_history import UploadHistory


def initialize_rag_system():
    """
    Initialize all RAG system components

    Returns:
        Tuple of (embedding_manager, vectorstore, rag_retriever, llm, upload_history)
    """
    print("=" * 60)
    print("Initializing UniGPT RAG System")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Initialize embedding manager
    print("\n[1/5] Initializing Embedding Manager...")
    embedding_manager = EmbeddingManager()

    # Initialize vector store
    print("\n[2/5] Initializing Vector Store...")
    vectorstore = VectorStore()

    # Initialize RAG retriever
    print("\n[3/5] Initializing RAG Retriever...")
    rag_retriever = RAGRetriever(vectorstore, embedding_manager)

    # Initialize upload history
    print("\n[4/5] Initializing Upload History...")
    upload_history = UploadHistory()

    # Initialize LLM
    print("\n[5/5] Initializing LLM...")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name='llama-3.1-8b-instant',
        temperature=0.1,
        max_tokens=1024
    )

    print("\n" + "=" * 60)
    print("✓ All components initialized successfully!")
    print("=" * 60)

    return embedding_manager, vectorstore, rag_retriever, llm, upload_history


def process_pdf_file(pdf_path: str, embedding_manager, vectorstore, upload_history):
    """
    Process a single PDF file and add it to the vector store

    Args:
        pdf_path: Path to the PDF file
        embedding_manager: EmbeddingManager instance
        vectorstore: VectorStore instance
        upload_history: UploadHistory instance
    """
    import time
    from pathlib import Path

    filepath = Path(pdf_path)
    if not filepath.exists():
        print(f"Error: File not found: {pdf_path}")
        return

    if not filepath.suffix.lower() == '.pdf':
        print(f"Error: Not a PDF file: {pdf_path}")
        return

    print(f"\nProcessing PDF: {filepath.name}")
    start_time = time.time()

    # Add to upload history
    upload_id = upload_history.add_upload(
        filename=filepath.name,
        original_filename=filepath.name,
        file_size=filepath.stat().st_size,
        status='processing'
    )

    try:
        # Process PDF
        num_pages, num_chunks = process_pdf(
            str(filepath),
            filepath.name,
            embedding_manager,
            vectorstore
        )

        processing_time = time.time() - start_time

        # Update upload history
        upload_history.update_upload_status(
            upload_id=upload_id,
            status='completed',
            num_pages=num_pages,
            num_chunks=num_chunks,
            processing_time=processing_time
        )

        print(f"✓ Successfully processed {filepath.name}")
        print(f"  - Pages: {num_pages}")
        print(f"  - Chunks: {num_chunks}")
        print(f"  - Processing time: {processing_time:.2f}s")

    except Exception as e:
        upload_history.update_upload_status(
            upload_id=upload_id,
            status='failed',
            error_message=str(e)
        )
        print(f"✗ Error processing {filepath.name}: {e}")


def query_rag_system(query: str, rag_retriever, llm, top_k: int = 3):
    """
    Query the RAG system and get an answer

    Args:
        query: Question to ask
        rag_retriever: RAGRetriever instance
        llm: Language model instance
        top_k: Number of documents to retrieve

    Returns:
        Answer string
    """
    print(f"\nQuery: {query}")
    print("-" * 60)

    answer = rag_simple(query, rag_retriever, llm, top_k=top_k)

    print(f"Answer: {answer}")
    print("-" * 60)

    return answer


def interactive_mode(rag_retriever, llm):
    """
    Run interactive Q&A session

    Args:
        rag_retriever: RAGRetriever instance
        llm: Language model instance
    """
    print("\n" + "=" * 60)
    print("Interactive Q&A Mode")
    print("Type 'exit' or 'quit' to end the session")
    print("=" * 60 + "\n")

    while True:
        try:
            query = input("You: ").strip()

            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            if not query:
                continue

            answer = rag_simple(query, rag_retriever, llm, top_k=3)
            print(f"\nAssistant: {answer}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == '__main__':
    # Initialize the system
    embedding_manager, vectorstore, rag_retriever, llm, upload_history = initialize_rag_system()

    # Example: Process a PDF file (uncomment to use)
    # process_pdf_file(
    #     "lecture_data/MRI/MRI - Lecture 1.pdf",
    #     embedding_manager,
    #     vectorstore,
    #     upload_history
    # )

    # Example: Query the system
    # query_rag_system(
    #     "What is MRI?",
    #     rag_retriever,
    #     llm,
    #     top_k=3
    # )

    # Start interactive mode
    interactive_mode(rag_retriever, llm)
