import React from 'react';
import './TypingDots.css';

/**
 * A simple animated typing indicator for bot replies.
 * Uses shared 'bubble bot' style for seamless integration.
 */
const TypingDots = () => (
  <div className="bubble bot">
    <div className="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
);

export default TypingDots;
