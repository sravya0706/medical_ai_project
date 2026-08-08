import { useState, useRef } from "react";
import "./ChatInput.css";

export default function ChatInput({ onSend, onSendImage, disabled }) {
  const [text, setText] = useState("");
  const fileInputRef = useRef(null);

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const caption = text.trim() || "Can you tell me what this looks like?";
    onSendImage(file, caption);
    setText("");
    e.target.value = "";
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <button
        type="button"
        className="chat-input__attach"
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled}
        aria-label="Attach a medical image"
        title="Attach a medical image"
      >
        +
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg"
        hidden
        onChange={handleFileChange}
      />
      <textarea
        className="chat-input__textarea"
        placeholder="Describe your symptoms…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={disabled}
      />
      <button type="submit" className="btn btn-primary chat-input__send" disabled={disabled || !text.trim()}>
        Send
      </button>
    </form>
  );
}
