import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import MessageBubble from "../components/MessageBubble";
import ChatInput from "../components/ChatInput";
import VitalLine from "../components/VitalLine";
import { useAuth } from "../context/AuthContext";
import { sendMessage, sendImage } from "../services/chatService";
import { getConversations, getConversation } from "../services/historyService";
import { extractErrorMessage } from "../services/api";
import "./ChatPage.css";

function decodeUserLabel(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub || "signed in";
  } catch {
    return "signed in";
  }
}

function newSessionId() {
  return crypto.randomUUID();
}

export default function ChatPage() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const [sessionId, setSessionId] = useState(newSessionId());
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [historyUnavailable, setHistoryUnavailable] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);

  const loadConversations = useCallback(async () => {
    try {
      const convos = await getConversations();
      setConversations(convos);
      setHistoryUnavailable(false);
    } catch (err) {
      // 503 = Mongo not reachable — documented, graceful degradation, not a crash
      setHistoryUnavailable(true);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  function handleNewChat() {
    setSessionId(newSessionId());
    setMessages([]);
    setActiveConversationId(null);
    setError("");
  }

  async function handleSelectConversation(conversationId) {
    setError("");
    try {
      const convo = await getConversation(conversationId);
      setActiveConversationId(conversationId);
      setMessages(
        (convo.messages || []).map((m) => ({
          role: m.role,
          content: m.content,
        }))
      );
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  async function runExchange(userMessage, apiCall) {
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setPending(true);
    setError("");

    try {
      const result = await apiCall();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.response,
          escalated: result.escalated,
          sources: result.sources,
          predictedConditions: result.predicted_conditions,
        },
      ]);
      loadConversations();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setPending(false);
    }
  }

  function handleSend(text) {
    runExchange(text, () => sendMessage(text, sessionId));
  }

  function handleSendImage(file, caption) {
    runExchange(`${caption} [image: ${file.name}]`, () => sendImage(file, caption, sessionId));
  }

  return (
    <div className="chat-page">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        historyUnavailable={historyUnavailable}
        userLabel={decodeUserLabel(token || "")}
        onLogout={() => {
          logout();
          navigate("/login");
        }}
      />

      <main className="chat-main">
        <div className="chat-main__scroll" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="chat-empty">
              <h2>How are you feeling today?</h2>
              <p>
                Describe your symptoms, or attach a photo of a rash, report, or
                prescription — MediAssist will look for grounded, relevant
                information before responding.
              </p>
            </div>
          ) : (
            messages.map((m, i) => <MessageBubble key={i} {...m} />)
          )}

          {pending && <VitalLine />}
          {error && <p className="chat-error error-text">{error}</p>}
        </div>

        <ChatInput onSend={handleSend} onSendImage={handleSendImage} disabled={pending} />
      </main>
    </div>
  );
}
