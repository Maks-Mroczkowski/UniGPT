import React, { useState, KeyboardEvent } from 'react';
import './InputBox.css';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const InputBox: React.FC<InputBoxProps> = ({ onSendMessage, disabled = false }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-box-container">
      <div className="input-box-wrapper">
        <div className="input-box">
          <textarea
            className="input-textarea"
            placeholder="Message UniGPT"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={disabled}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!input.trim() || disabled}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <div className="input-info">
          UniGPT is designed with Uni in mind.
        </div>
      </div>
    </div>
  );
};

export default InputBox;
