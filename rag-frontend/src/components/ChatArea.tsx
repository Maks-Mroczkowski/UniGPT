import React, { useState } from 'react';
import InputBox from './InputBox';
import MessageList from './MessageList';
import FileUpload from './FileUpload';
import UploadHistory from './UploadHistory';
import './ChatArea.css';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const ChatArea: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState(0);

  const handleSendMessage = async (content: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
    };
    setMessages(prev => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          top_k: 3,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running on http://localhost:5001',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setRefreshHistory(prev => prev + 1);
  };

  return (
    <div className="chat-area">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="welcome-header">
            <h1 className="welcome-title">UniGPT</h1>
            <p className="welcome-subtitle">How can I help you today?</p>
          </div>

          <div className="welcome-content">
            <div className="upload-section">
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>

            <div className="history-section">
              <UploadHistory refreshTrigger={refreshHistory} />
            </div>
          </div>
        </div>
      ) : (
        <MessageList messages={messages} isLoading={isLoading} />
      )}
      <InputBox onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatArea;
