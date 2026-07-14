import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const askAI = async () => {
    if (!question.trim()) return;

    const userQuestion = question;

    // Show user message immediately
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/ask",
        {
          params: {
            question: userQuestion,
          },
        }
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.data.answer,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "❌ Unable to connect to AI service.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🏥 Medical AI Assistant</h1>

      <div className="chat-box">
        {messages.length === 0 && (
          <p className="welcome">
            Ask any healthcare-related question.
          </p>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={
              msg.role === "user"
                ? "user-message"
                : "assistant-message"
            }
          >
            <strong>
              {msg.role === "user" ? "👤 You" : "🤖 AI"}
            </strong>

            <p>{msg.content}</p>
          </div>
        ))}

        {loading && (
          <div className="assistant-message">
            <strong>🤖 AI</strong>
            <p>Thinking...</p>
          </div>
        )}
      </div>

      <div className="input-container">
        <input
          type="text"
          placeholder="Ask a medical question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") askAI();
          }}
        />

        <button onClick={askAI}>
          Ask AI
        </button>
      </div>
    </div>
  );
}

export default App;