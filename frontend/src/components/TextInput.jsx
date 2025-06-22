import React, { useState } from 'react';
import './TextInput.css';

const TextInput = ({ onSend }) => {
  const [input, setInput] = useState("");

  // Submit text to parent and clear input
  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  // Allow Enter key to send
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit();
  };

  return (
    <div className="text-input-container">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        aria-label="Type your message"
      />
      <button onClick={handleSubmit} aria-label="Send message">Send</button>
    </div>
  );
};

export default TextInput;
