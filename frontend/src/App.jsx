import React, { useState, useRef } from 'react';
import ChatBubble from './components/ChatBubble';
import TypingDots from './components/TypingDots';
import Recorder from './components/Recorder';
import TextInput from './components/TextInput';
import './App.css';
import logo from './assets/logo.png';
import talkingGif from './assets/therapist-talking.gif';
import stillImage from './assets/therapist-still.gif';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [mode, setMode] = useState("voice");
  const chatRef = useRef(null);

  const toggleMode = () => setMode((prev) => (prev === "voice" ? "text" : "voice"));

  // Animate typing effect
  const appendTypingMessage = (fullText, role, emotion = '') => {
    return new Promise(resolve => {
      const newMessage = { role, text: '', emotion };
      setMessages(prev => [...prev, newMessage]);

      let index = 0;
      const interval = setInterval(() => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            text: fullText.slice(0, index + 1),
          };
          return updated;
        });

        index++;
        if (index >= fullText.length) {
          clearInterval(interval);
          resolve();
        }
      }, 20);
    });
  };

  // Shared logic for playing response audio and displaying text
  const playAndDisplayReply = async (replyText, replyAudioUrl, emotion) => {
    await new Promise(resolve => setTimeout(resolve, 500));

    const audio = new Audio(`http://localhost:8000${replyAudioUrl}`);
    setIsSpeaking(true);
    audio.play();
    audio.onended = () => setIsSpeaking(false);

    await appendTypingMessage(replyText, 'bot', emotion);
  };

  // Voice mode handler
  const handleResponse = async (audioBlob) => {
    const formData = new FormData();
    formData.append("audio", audioBlob, "input.wav");

    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/talk/", {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'user',
        text: data.transcript,
        emotion: data.emotion
      }]);

      await playAndDisplayReply(data.reply_text, data.reply_audio_url, data.emotion);

    } catch (err) {
      console.error("Error:", err);
      setIsSpeaking(false);
    } finally {
      setIsTyping(false);
    }
  };

  // Text mode handler
  const handleTextInput = async (text) => {
    setMessages(prev => [...prev, { role: 'user', text, emotion: '' }]);
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/text-talk/", {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });

      const data = await res.json();

      await playAndDisplayReply(data.reply_text, data.reply_audio_url, data.emotion);
    } catch (err) {
      console.error("Error:", err);
      setIsSpeaking(false);
    } finally {
      setIsTyping(false);
    }
  };

  // -----------------
  // 🎨 UI Render
  // -----------------
  return (
    <div className="app">
      <div className="left-panel">
        <div className="brand-banner">
          <div className="brand-section">
            <div className="brand-header">
              <h1 className="brand-title">Psyche Mend</h1>
              <img src={logo} alt="Psyche Mend Logo" className="brand-logo" />
            </div>
            <p className="tagline">Your emotional well-being, supported by AI</p>
          </div>
        </div>

        <div className="chat-window" ref={chatRef}>
          {messages.map((msg, i) => (
            <ChatBubble key={i} role={msg.role} text={msg.text} emotion={msg.emotion} />
          ))}
          {isTyping && <TypingDots />}
        </div>
      </div>

      <div className="right-panel">
        <div className="therapist-container">
          <img
            src={isSpeaking ? talkingGif : stillImage}
            alt="Therapist avatar"
            className={`therapist-avatar ${isSpeaking ? 'speaking' : ''}`}
          />
        </div>

        <div className="controls">
          <button onClick={toggleMode}>
            {mode === "voice" ? "Switch to Text" : "Switch to Voice 🎙️"}
          </button>
          {mode === "voice" ? (
            <Recorder onStop={handleResponse} />
          ) : (
            <TextInput onSend={handleTextInput} />
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
