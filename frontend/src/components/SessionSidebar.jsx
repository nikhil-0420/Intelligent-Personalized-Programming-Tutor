import { useState } from "react";
import { getSessionMessages, deleteSession } from "../api";
import { Trash2 } from "lucide-react";

const COLLAPSED_WIDTH = 52;
const EXPANDED_WIDTH = 240;

export default function SessionSidebar({
  sessions, activeSessionId, onNewChat, onSelectSession, onSessionsChanged, onDeleteSession,
}) {
  const [pinned, setPinned] = useState(false);
  const [hovering, setHovering] = useState(false);

  const expanded = pinned || hovering;

  const handleClick = async (session) => {
    try {
      const msgs = await getSessionMessages(session.id);
      onSelectSession(session, msgs);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (e, session) => {
    e.stopPropagation(); // don't also trigger handleClick
    if (!window.confirm(`Delete "${session.title}"? This can't be undone.`)) return;
    try {
      await deleteSession(session.id);
      onDeleteSession(session.id);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <div style={{ width: pinned ? EXPANDED_WIDTH : COLLAPSED_WIDTH, flexShrink: 0 }} />

      <div
        onMouseEnter={() => setHovering(true)}
        onMouseLeave={() => setHovering(false)}
        style={{ width: expanded ? EXPANDED_WIDTH : COLLAPSED_WIDTH }}
        className={`fixed top-[100px] bottom-8 z-20 overflow-hidden transition-all duration-150 ease-out ${
          expanded ? "rounded-xl border border-text/10 bg-surface shadow-xl" : "border-transparent bg-transparent"
        }`}
      >
        <div style={{ width: EXPANDED_WIDTH }} className="flex h-full flex-col p-2">
          <button
            onClick={() => setPinned((p) => !p)}
            className={`mb-1 flex items-center gap-2 rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors ${
              pinned ? "bg-pine/10 text-pine" : "text-muted hover:bg-base hover:text-text"
            }`}
            title={pinned ? "Collapse sidebar" : "Keep sidebar open"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="shrink-0">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
              <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            {expanded && <span>Chats</span>}
          </button>

          <button
            onClick={onNewChat}
            className="mb-2 flex items-center gap-2 rounded-lg px-2.5 py-2 text-left text-xs font-medium text-text hover:bg-base"
            title="New chat"
          >
            <span className="w-4 shrink-0 text-center text-base leading-none">+</span>
            {expanded && <span>New chat</span>}
          </button>

          <div className="flex min-h-0 flex-1 flex-col gap-0.5 overflow-y-auto">
            {expanded &&
              sessions.map((s) => (
                <div
                  key={s.id}
                  onClick={() => handleClick(s)}
                  className={`group flex items-center justify-between rounded-lg px-2.5 py-2 text-xs cursor-pointer ${
                    s.id === activeSessionId
                      ? "bg-pine/10 text-pine"
                      : "text-muted hover:bg-base hover:text-text"
                  }`}
                  title={s.title}
                >
                  <span className="truncate">{s.title}</span>
                  <button
                    onClick={(e) => handleDelete(e, s)}
                    className="ml-1 shrink-0 rounded p-0.5 opacity-0 hover:text-clay group-hover:opacity-100"
                    title="Delete chat"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            {expanded && sessions.length === 0 && (
              <div className="px-2.5 py-2 text-xs text-muted">No past chats yet</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}