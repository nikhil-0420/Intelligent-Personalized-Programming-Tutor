import { useState, useEffect } from "react";
import { listSessions, getSessionMessages } from "../api";

const COLLAPSED_WIDTH = 52;
const EXPANDED_WIDTH = 240;

export default function SessionSidebar({ studentId, activeSessionId, onNewChat, onSelectSession, refreshKey }) {
    const [sessions, setSessions] = useState([]);
    const [pinned, setPinned] = useState(false);
    const [hovering, setHovering] = useState(false);

    const expanded = pinned || hovering;

    useEffect(() => {
        listSessions(studentId).then(setSessions).catch(console.error);
    }, [studentId, refreshKey]);

    const handleClick = async (session) => {
        try {
            const msgs = await getSessionMessages(session.id);
            onSelectSession(session, msgs);
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
                className={`fixed top-[100px] bottom-8 z-20 overflow-hidden transition-all duration-150 ease-out ${expanded ? "rounded-xl border border-text/10 bg-surface shadow-xl" : "border-transparent bg-transparent"
                    }`}
            >
                <div style={{ width: EXPANDED_WIDTH }} className="flex h-full flex-col p-2">
                    {/* Icon-only rail item -- click toggles pin, same element whether collapsed or expanded */}
                    <button
                        onClick={() => setPinned((p) => !p)}
                        className={`mb-1 flex items-center gap-2 rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors ${pinned ? "bg-pine/10 text-pine" : "text-muted hover:bg-base hover:text-text"
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

                    <div className="flex flex-1 flex-col gap-0.5 overflow-y-auto">
                        {expanded &&
                            sessions.map((s) => (
                                <button
                                    key={s.id}
                                    onClick={() => handleClick(s)}
                                    className={`truncate rounded-lg px-2.5 py-2 text-left text-xs ${s.id === activeSessionId
                                        ? "bg-pine/10 text-pine"
                                        : "text-muted hover:bg-base hover:text-text"
                                        }`}
                                    title={s.title}
                                >
                                    {s.title}
                                </button>
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