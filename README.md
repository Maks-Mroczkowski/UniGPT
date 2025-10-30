# UniGPT

A Retrieval-Augmented Generation (RAG) system built with Flask, React, and ChromaDB. Upload PDF documents, and ask questions about them using natural language.

## Features

- **PDF Upload**: Drag-and-drop interface for uploading PDF documents
- **Automatic Processing**: PDFs are automatically chunked, embedded, and indexed
- **Vector Search**: Powered by ChromaDB for fast similarity search
- **LLM Integration**: Uses Groq's LLaMA 3.1 for answer generation
- **Upload History**: Track all uploaded documents with metadata
- **Modern UI**: Clean, dark-themed React interface

## Architecture

### Backend (Python/Flask)
- **Embedding Model**: SentenceTransformer (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB with persistent storage
- **LLM**: Groq LLaMA 3.1-8b-instant
- **Document Processing**: LangChain for PDF loading and chunking

### Frontend (React/TypeScript)
- Modern, responsive UI
- Drag-and-drop file upload
- Real-time chat interface
- Upload history tracking

## Project Structure

```
UniGPT/
├── RAG/                        # Backend
│   ├── api.py                  # Flask API server
│   ├── main.py                 # Standalone usage example
│   ├── embedding_manager.py    # Embedding generation
│   ├── vector_store.py         # Vector database management
│   ├── rag_retriever.py        # Retrieval & answer generation
│   ├── pdf_processor.py        # PDF processing pipeline
│   ├── upload_history.py       # Upload tracking
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
│
├── rag-frontend/               # Frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ChatArea.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── UploadHistory.tsx
│   │   │   ├── InputBox.tsx
│   │   │   └── MessageList.tsx
│   │   └── App.tsx
│   └── package.json
│
├── Vector_store/               # ChromaDB storage (generated)
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Groq API Key ([Get one here](https://console.groq.com/))

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd RAG
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Add your Groq API key to `.env`:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd rag-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

### Start the Backend

```bash
cd RAG
python api.py
```

The API will be available at `http://localhost:5001`

### Start the Frontend

```bash
cd rag-frontend
npm start
```

The application will open at `http://localhost:3000`

### Using the Application

1. **Upload PDFs**: Drag and drop PDF files onto the upload area
2. **Wait for Processing**: The system will chunk and index your document
3. **Ask Questions**: Type questions in the chat interface
4. **View History**: See all uploaded documents in the history section

### Standalone Mode (Python)

You can also use the backend directly:

```bash
cd RAG
python main.py
```

This starts an interactive Q&A session in your terminal.

## API Endpoints

### `GET /api/health`
Health check endpoint

### `POST /api/chat`
Send a message and get a response
```json
{
  "message": "What is MRI?",
  "top_k": 3
}
```

### `POST /api/upload`
Upload a PDF file (multipart/form-data)

### `GET /api/uploads`
Get upload history

### `GET /api/uploads/stats`
Get upload statistics

## Configuration

### Backend Configuration

Edit `api.py` or `main.py`:

- **Chunk Size**: Default 400 characters (in `pdf_processor.py`)
- **Chunk Overlap**: Default 200 characters
- **Top-K Retrieval**: Default 3 documents
- **LLM Temperature**: Default 0.1
- **Max Tokens**: Default 1024

### Frontend Configuration

Edit API URL in component files if needed:
```typescript
const API_URL = 'http://localhost:5001';
```

## Development

### Adding New Features

The modular architecture makes it easy to extend:

- **New Document Types**: Modify `pdf_processor.py`
- **Different Embeddings**: Change model in `embedding_manager.py`
- **Alternative Vector DB**: Replace `vector_store.py`
- **Different LLM**: Update LLM initialization in `api.py`

### Testing

Run syntax checks:
```bash
cd RAG
python -m py_compile *.py
```

## Technologies Used

### Backend
- Flask & Flask-CORS
- LangChain & LangChain-Community
- ChromaDB
- SentenceTransformers
- Groq API
- PyPDF & PyMuPDF

### Frontend
- React 19
- TypeScript
- CSS3

## Security Notes

- **Never commit your `.env` file** - it contains sensitive API keys
- The `.gitignore` is configured to exclude sensitive files
- Use environment variables for all secrets
- Consider rate limiting for production deployments

## Troubleshooting

### Backend won't start
- Check if port 5001 is available
- Verify GROQ_API_KEY is set in `.env`
- Ensure all dependencies are installed

### Frontend can't connect
- Verify backend is running on port 5001
- Check CORS settings in `api.py`
- Clear browser cache

### PDF processing fails
- Check PDF is not password-protected
- Ensure sufficient disk space for vector store
- Verify PDF is not corrupted

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- LangChain for document processing tools
- ChromaDB for vector storage
- Groq for LLM API access
- SentenceTransformers for embeddings
