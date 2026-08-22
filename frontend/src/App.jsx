import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import SessionSidebar from "./components/SessionSidebar";
import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import EvaluationPage from "./pages/EvaluationPage";
import { listSessions } from "./api";
import { useNavigate } from "react-router-dom";

const STUDENT_ID = 1;

function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const showSidebar = location.pathname === "/chat";

  const [messages, setMessages] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [lastTrace, setLastTrace] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [chatInstanceKey, setChatInstanceKey] = useState(0);
  const [sessions, setSessions] = useState([]);

  const refreshSessions = () => {
    listSessions(STUDENT_ID).then(setSessions).catch(console.error);
  };

  useEffect(() => {
    refreshSessions();
  }, []);

  const activeSessionTitle = sessions.find((s) => s.id === sessionId)?.title || null;

  const startNewChat = () => {
    setMessages([]);
    setSelectedTopic("");
    setLastTrace(null);
    setSessionId(null);
    setChatInstanceKey((k) => k + 1);
  };

  const loadSession = (session, sessionMessages) => {
    setSessionId(session.id);
    setChatInstanceKey((k) => k + 1);
    setSelectedTopic(sessionMessages[0]?.topic_slug || "");
    setMessages(
      sessionMessages.flatMap((m) => [
        { role: "student", text: m.student_input },
        {
          role: "tutor",
          text: m.tutor_response,
          trace: m.agent_trace,
          interactionId: m.id,
          feedback: m.feedback,
          pKnowBefore: m.p_know_before,
          pKnowAfter: m.p_know_after,
        },
      ])
    );
    setLastTrace(sessionMessages[sessionMessages.length - 1]?.agent_trace || null);
  };

  const handleDeleteSession = (deletedId) => {
    setSessions((prev) => prev.filter((s) => s.id !== deletedId));
    if (deletedId === sessionId) {
      startNewChat();
    }
  };

  return (
    <div className="min-h-screen bg-base px-6 py-10">
      <div className="mx-auto max-w-[1440px]">
        <NavBar sessionTitle={showSidebar ? activeSessionTitle : null} />
        <div className="mt-6 flex gap-6">
          {showSidebar && (
            <SessionSidebar
              sessions={sessions}
              activeSessionId={sessionId}
              onNewChat={startNewChat}
              onSelectSession={loadSession}
              onSessionsChanged={refreshSessions}
              onDeleteSession={handleDeleteSession}
            />
          )}
          <div className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route
                path="/chat"
                element={
                  <ChatPage
                    key={chatInstanceKey}
                    messages={messages}
                    setMessages={setMessages}
                    selectedTopic={selectedTopic}
                    setSelectedTopic={setSelectedTopic}
                    lastTrace={lastTrace}
                    setLastTrace={setLastTrace}
                    sessionId={sessionId}
                    setSessionId={setSessionId}
                    onSessionCreated={refreshSessions}
                  />
                }
              />
              <Route path="/evaluation" element={<EvaluationPage />} />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}