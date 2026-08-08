import "./MessageBubble.css";

export default function MessageBubble({ role, content, escalated, sources, predictedConditions }) {
  const isUser = role === "user";

  return (
    <div className={`bubble-row ${isUser ? "bubble-row--user" : "bubble-row--assistant"}`}>
      <div
        className={`bubble ${isUser ? "bubble--user" : "bubble--assistant"} ${
          escalated ? "bubble--escalated" : ""
        }`}
      >
        {escalated && <div className="bubble__escalation-label mono">EMERGENCY GUIDANCE</div>}
        <p className="bubble__text">{content}</p>

        {predictedConditions?.length > 0 && (
          <div className="bubble__meta">
            <span className="bubble__meta-label mono">possible conditions</span>
            <div className="bubble__tags">
              {predictedConditions.map((c) => (
                <span key={c.condition} className="tag mono">
                  {c.condition} · {Math.round(c.confidence * 100)}%
                </span>
              ))}
            </div>
          </div>
        )}

        {sources?.length > 0 && (
          <div className="bubble__meta">
            <span className="bubble__meta-label mono">sources</span>
            <div className="bubble__tags">
              {sources.map((s, i) => (
                <span key={`${s}-${i}`} className="tag tag--muted mono">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
