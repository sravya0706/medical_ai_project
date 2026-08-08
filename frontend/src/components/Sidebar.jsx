import "./Sidebar.css";

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  historyUnavailable,
  userLabel,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-mark">M</span>
        <span className="sidebar__brand-name">MediAssist</span>
      </div>

      <button className="btn btn-primary sidebar__new-chat" onClick={onNewChat}>
        New conversation
      </button>

      <div className="sidebar__section-label mono">history</div>

      {historyUnavailable ? (
        <p className="sidebar__empty-note">
          Conversation history isn't available right now — the database
          connection isn't reachable. You can still chat; this session just
          won't be saved.
        </p>
      ) : conversations.length === 0 ? (
        <p className="sidebar__empty-note">Your past conversations will appear here.</p>
      ) : (
        <ul className="sidebar__list">
          {conversations.map((c) => (
            <li key={c._id}>
              <button
                className={`sidebar__item ${c._id === activeConversationId ? "sidebar__item--active" : ""}`}
                onClick={() => onSelectConversation(c._id)}
              >
                {c.title || "Untitled conversation"}
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="sidebar__footer">
        <span className="mono sidebar__user">{userLabel}</span>
        <button className="btn btn-ghost sidebar__logout" onClick={onLogout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
