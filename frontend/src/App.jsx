import { useState } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import SessionSidebar from "./components/SessionSidebar";
import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import EvaluationPage from "./pages/EvaluationPage";

const STUDENT_ID = 1;

function AppLayout() {
  const location = useLocation();
  const showSidebar = location.pathname === "/chat";

  const [messages, setMessages] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [lastTrace, setLastTrace] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionRefreshKey, setSessionRefreshKey] = useState(0);

  const startNewChat = () => {
    setMessages([]);
    setSelectedTopic("");
    setLastTrace(null);
    setSessionId(null);
  };

  const loadSession = (session, sessionMessages) => {
    setSessionId(session.id);
    setSelectedTopic(sessionMessages[0]?.topic_slug || "");
    setMessages(
      sessionMessages.flatMap((m) => [
        { role: "student", text: m.student_input },
        { role: "tutor", text: m.tutor_response, trace: m.agent_trace },
      ])
    );
    setLastTrace(sessionMessages[sessionMessages.length - 1]?.agent_trace || null);
  };

  return (
    <div className="min-h-screen bg-base px-6 py-10">
      <div className="mx-auto max-w-[1440px]">
        <NavBar />
        <div className="mt-6 flex gap-6">
          {showSidebar && (
            <SessionSidebar
              studentId={STUDENT_ID}
              activeSessionId={sessionId}
              onNewChat={startNewChat}
              onSelectSession={loadSession}
              refreshKey={sessionRefreshKey}
            />
          )}
          <div className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route
                path="/chat"
                element={
                  <ChatPage
                    messages={messages}
                    setMessages={setMessages}
                    selectedTopic={selectedTopic}
                    setSelectedTopic={setSelectedTopic}
                    lastTrace={lastTrace}
                    setLastTrace={setLastTrace}
                    sessionId={sessionId}
                    setSessionId={setSessionId}
                    onSessionCreated={() => setSessionRefreshKey((k) => k + 1)}
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