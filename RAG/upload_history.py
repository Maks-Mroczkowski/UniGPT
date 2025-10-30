"""
Upload history database management for UniGPT
Tracks all PDF uploads and their processing status
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class UploadHistory:
    """Manages upload history using SQLite database"""

    def __init__(self, db_path: str = "../Vector_store/upload_history.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Create the upload history table if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                upload_timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                num_pages INTEGER,
                num_chunks INTEGER,
                processing_time_seconds REAL,
                error_message TEXT
            )
        """)

        conn.commit()
        conn.close()
        print(f"Upload history database initialized at: {self.db_path}")

    def add_upload(
        self,
        filename: str,
        original_filename: str,
        file_size: int,
        status: str = "processing",
        num_pages: Optional[int] = None,
        num_chunks: Optional[int] = None,
        processing_time: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> int:
        """Add a new upload record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO uploads (
                filename, original_filename, file_size, upload_timestamp,
                status, num_pages, num_chunks, processing_time_seconds, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, original_filename, file_size, timestamp,
            status, num_pages, num_chunks, processing_time, error_message
        ))

        upload_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return upload_id

    def update_upload_status(
        self,
        upload_id: int,
        status: str,
        num_pages: Optional[int] = None,
        num_chunks: Optional[int] = None,
        processing_time: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """Update an existing upload record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE uploads
            SET status = ?,
                num_pages = COALESCE(?, num_pages),
                num_chunks = COALESCE(?, num_chunks),
                processing_time_seconds = COALESCE(?, processing_time_seconds),
                error_message = COALESCE(?, error_message)
            WHERE id = ?
        """, (status, num_pages, num_chunks, processing_time, error_message, upload_id))

        conn.commit()
        conn.close()

    def get_all_uploads(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all upload records, most recent first"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM uploads
            ORDER BY upload_timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_upload_by_id(self, upload_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific upload record by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM uploads WHERE id = ?", (upload_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_statistics(self) -> Dict[str, Any]:
        """Get upload statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total uploads
        cursor.execute("SELECT COUNT(*) FROM uploads")
        total_uploads = cursor.fetchone()[0]

        # Successful uploads
        cursor.execute("SELECT COUNT(*) FROM uploads WHERE status = 'completed'")
        successful_uploads = cursor.fetchone()[0]

        # Failed uploads
        cursor.execute("SELECT COUNT(*) FROM uploads WHERE status = 'failed'")
        failed_uploads = cursor.fetchone()[0]

        # Total pages processed
        cursor.execute("SELECT SUM(num_pages) FROM uploads WHERE status = 'completed'")
        total_pages = cursor.fetchone()[0] or 0

        # Total chunks created
        cursor.execute("SELECT SUM(num_chunks) FROM uploads WHERE status = 'completed'")
        total_chunks = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_uploads': total_uploads,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'total_pages_processed': total_pages,
            'total_chunks_created': total_chunks
        }
