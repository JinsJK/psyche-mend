import React, { useState, useRef } from 'react';
import './Recorder.css';

const Recorder = ({ onStop }) => {
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const [recording, setRecording] = useState(false);

  // Start recording on hold
  const startRecording = async () => {
    setRecording(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = e => chunks.current.push(e.data);
      mediaRecorder.current.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/wav' });
        chunks.current = [];
        onStop(blob);
      };

      mediaRecorder.current.start();
    } catch (err) {
      console.error("Microphone access denied:", err);
      setRecording(false);
    }
  };

  // Stop recording when button released
  const stopRecording = () => {
    if (mediaRecorder.current && recording) {
      mediaRecorder.current.stop();
      setRecording(false);
    }
  };

  return (
    <button
      className={`record-btn ${recording ? 'recording' : ''}`}
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
      onTouchStart={startRecording}
      onTouchEnd={stopRecording}
      aria-label="Hold to talk"
    >
      {recording ? (
        <span className="active-text">🎧 Listening...</span>
      ) : (
        <span>🎙️ Hold to Talk</span>
      )}
    </button>
  );
};

export default Recorder;
