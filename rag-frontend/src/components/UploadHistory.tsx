import React, { useState, useEffect } from 'react';
import './UploadHistory.css';

interface Upload {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  upload_timestamp: string;
  status: string;
  num_pages: number | null;
  num_chunks: number | null;
  processing_time_seconds: number | null;
  error_message: string | null;
}

interface UploadHistoryProps {
  refreshTrigger?: number;
}

const UploadHistory: React.FC<UploadHistoryProps> = ({ refreshTrigger = 0 }) => {
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUploads = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5001/api/uploads');
      const data = await response.json();

      if (response.ok && data.status === 'success') {
        setUploads(data.uploads);
        setError(null);
      } else {
        setError('Failed to load upload history');
      }
    } catch (err) {
      setError('Network error. Please ensure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUploads();
  }, [refreshTrigger]);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (isoString: string): string => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="status-icon success" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return (
          <div className="status-icon processing">
            <div className="processing-spinner"></div>
          </div>
        );
      case 'failed':
        return (
          <svg className="status-icon error" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  if (loading && uploads.length === 0) {
    return (
      <div className="upload-history-container">
        <h3 className="upload-history-title">Upload History</h3>
        <div className="upload-history-loading">
          <div className="spinner"></div>
          <p>Loading upload history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="upload-history-container">
        <h3 className="upload-history-title">Upload History</h3>
        <div className="upload-history-error">
          <p>{error}</p>
          <button onClick={fetchUploads} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="upload-history-container">
      <div className="upload-history-header">
        <h3 className="upload-history-title">Upload History</h3>
        <button onClick={fetchUploads} className="refresh-button" title="Refresh">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {uploads.length === 0 ? (
        <div className="upload-history-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No uploads yet</p>
          <span>Upload your first PDF to get started</span>
        </div>
      ) : (
        <div className="upload-history-list">
          {uploads.map((upload) => (
            <div key={upload.id} className={`upload-item ${upload.status}`}>
              <div className="upload-item-icon">
                {getStatusIcon(upload.status)}
              </div>
              <div className="upload-item-content">
                <div className="upload-item-header">
                  <span className="upload-filename" title={upload.original_filename}>
                    {upload.original_filename}
                  </span>
                  <span className="upload-time">{formatDate(upload.upload_timestamp)}</span>
                </div>
                <div className="upload-item-details">
                  <span>{formatFileSize(upload.file_size)}</span>
                  {upload.num_pages && (
                    <>
                      <span>•</span>
                      <span>{upload.num_pages} pages</span>
                    </>
                  )}
                  {upload.num_chunks && (
                    <>
                      <span>•</span>
                      <span>{upload.num_chunks} chunks</span>
                    </>
                  )}
                  {upload.processing_time_seconds && (
                    <>
                      <span>•</span>
                      <span>{upload.processing_time_seconds.toFixed(1)}s</span>
                    </>
                  )}
                </div>
                {upload.error_message && (
                  <div className="upload-error-message">
                    {upload.error_message}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadHistory;
