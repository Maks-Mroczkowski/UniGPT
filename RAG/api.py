"""
UniGPT API Server
Main Flask application for the UniGPT RAG system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import time

# Import custom modules
from embedding_manager import EmbeddingManager
from vector_store import VectorStore
from rag_retriever import RAGRetriever, rag_simple
from pdf_processor import process_pdf
from upload_history import UploadHistory

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize global variables
embedding_manager = None
vectorstore = None
rag_retriever = None
llm = None
upload_history = None

# Upload configuration
UPLOAD_FOLDER = Path("./uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'UniGPT API is running',
        'vector_store_count': vectorstore.collection.count() if vectorstore else 0
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message']
        top_k = data.get('top_k', 3)  # Number of relevant documents to retrieve

        # Generate answer using RAG
        answer = rag_simple(user_message, rag_retriever, llm, top_k=top_k)

        return jsonify({
            'response': answer,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Upload and process a PDF file"""
    start_time = time.time()

    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check if file is PDF
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Save file
        original_filename = secure_filename(file.filename)
        timestamp = int(time.time())
        filename = f"{timestamp}_{original_filename}"
        filepath = UPLOAD_FOLDER / filename

        file.save(str(filepath))
        file_size = filepath.stat().st_size

        # Create upload history record
        upload_id = upload_history.add_upload(
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            status='processing'
        )

        # Process PDF
        try:
            num_pages, num_chunks = process_pdf(
                str(filepath),
                original_filename,
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

            return jsonify({
                'status': 'success',
                'message': 'PDF uploaded and processed successfully',
                'upload_id': upload_id,
                'filename': original_filename,
                'num_pages': num_pages,
                'num_chunks': num_chunks,
                'processing_time': round(processing_time, 2)
            })

        except Exception as e:
            error_message = str(e)
            print(f"Error processing PDF: {error_message}")

            # Update upload history with error
            upload_history.update_upload_status(
                upload_id=upload_id,
                status='failed',
                error_message=error_message
            )

            return jsonify({
                'status': 'error',
                'error': error_message
            }), 500

    except Exception as e:
        print(f"Error handling upload: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/uploads', methods=['GET'])
def get_uploads():
    """Get upload history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        uploads = upload_history.get_all_uploads(limit=limit)

        return jsonify({
            'status': 'success',
            'uploads': uploads
        })

    except Exception as e:
        print(f"Error retrieving uploads: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/uploads/stats', methods=['GET'])
def get_upload_stats():
    """Get upload statistics"""
    try:
        stats = upload_history.get_statistics()

        return jsonify({
            'status': 'success',
            'statistics': stats
        })

    except Exception as e:
        print(f"Error retrieving stats: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


def initialize_services():
    """Initialize all services on startup"""
    global embedding_manager, vectorstore, rag_retriever, llm, upload_history

    print("Initializing UniGPT services...")

    # Initialize embedding manager
    embedding_manager = EmbeddingManager()

    # Initialize vector store
    vectorstore = VectorStore()

    # Initialize RAG retriever
    rag_retriever = RAGRetriever(vectorstore, embedding_manager)

    # Initialize upload history
    upload_history = UploadHistory()

    # Initialize LLM
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

    print("All services initialized successfully!")


if __name__ == '__main__':
    initialize_services()
    print("\n🚀 Starting UniGPT API server...")
    print("📍 API will be available at: http://localhost:5001")
    print("📍 Health check: http://localhost:5001/api/health")
    print("📍 Chat endpoint: http://localhost:5001/api/chat\n")
    app.run(debug=True, port=5001, host='0.0.0.0')
