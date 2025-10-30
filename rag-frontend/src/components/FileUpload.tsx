import React, { useState, useRef } from 'react';
import './FileUpload.css';

interface FileUploadProps {
  onUploadSuccess?: () => void;
  onUploadError?: (error: string) => void;
}

interface UploadStatus {
  status: 'idle' | 'uploading' | 'success' | 'error';
  message?: string;
  filename?: string;
  numPages?: number;
  numChunks?: number;
  processingTime?: number;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onUploadError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ status: 'idle' });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        uploadFile(file);
      } else {
        setUploadStatus({
          status: 'error',
          message: 'Only PDF files are allowed'
        });
        onUploadError?.('Only PDF files are allowed');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        uploadFile(file);
      } else {
        setUploadStatus({
          status: 'error',
          message: 'Only PDF files are allowed'
        });
        onUploadError?.('Only PDF files are allowed');
      }
    }
  };

  const uploadFile = async (file: File) => {
    setUploadStatus({
      status: 'uploading',
      message: 'Uploading and processing PDF...',
      filename: file.name
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5001/api/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        setUploadStatus({
          status: 'success',
          message: 'PDF processed successfully!',
          filename: data.filename,
          numPages: data.num_pages,
          numChunks: data.num_chunks,
          processingTime: data.processing_time
        });
        onUploadSuccess?.();

        // Reset after 3 seconds
        setTimeout(() => {
          setUploadStatus({ status: 'idle' });
        }, 3000);
      } else {
        const errorMsg = data.error || 'Failed to upload PDF';
        setUploadStatus({
          status: 'error',
          message: errorMsg
        });
        onUploadError?.(errorMsg);
      }
    } catch (error) {
      const errorMsg = 'Network error. Please ensure the server is running.';
      setUploadStatus({
        status: 'error',
        message: errorMsg
      });
      onUploadError?.(errorMsg);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-container">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${uploadStatus.status}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {uploadStatus.status === 'idle' && (
          <div className="drop-zone-content">
            <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="drop-zone-title">Drop PDF here or click to browse</p>
            <p className="drop-zone-subtitle">Only PDF files are supported</p>
          </div>
        )}

        {uploadStatus.status === 'uploading' && (
          <div className="drop-zone-content">
            <div className="spinner"></div>
            <p className="drop-zone-title">{uploadStatus.message}</p>
            {uploadStatus.filename && (
              <p className="drop-zone-subtitle">{uploadStatus.filename}</p>
            )}
          </div>
        )}

        {uploadStatus.status === 'success' && (
          <div className="drop-zone-content">
            <svg className="success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="drop-zone-title">{uploadStatus.message}</p>
            <div className="upload-stats">
              <span>{uploadStatus.numPages} pages</span>
              <span>•</span>
              <span>{uploadStatus.numChunks} chunks</span>
              <span>•</span>
              <span>{uploadStatus.processingTime}s</span>
            </div>
          </div>
        )}

        {uploadStatus.status === 'error' && (
          <div className="drop-zone-content">
            <svg className="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="drop-zone-title">Upload Failed</p>
            <p className="drop-zone-subtitle">{uploadStatus.message}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
