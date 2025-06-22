import React from 'react';
import './ChatBubble.css';
import userIcon from '../assets/user.png';
import botIcon from '../assets/therapist.png';

const ChatBubble = ({ role, text, emotion }) => {
  const isUser = role === 'user';
  const icon = isUser ? userIcon : botIcon;
  const altText = isUser ? 'User avatar' : 'Therapist avatar';

  return (
    <div className={`bubble-wrapper ${role}`}>
      {/* Left or right aligned based on user/bot */}
      {isUser ? (
        <>
          <div className={`bubble ${role}`}>
            <div className="text">{text}</div>
          </div>
          <img src={icon} alt={altText} className="bubble-avatar" />
        </>
      ) : (
        <>
          <img src={icon} alt={altText} className="bubble-avatar" />
          <div className={`bubble ${role}`}>
            <div className="text">{text}</div>
            <div className="emotion">Detected Emotion: {emotion}</div>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatBubble;
