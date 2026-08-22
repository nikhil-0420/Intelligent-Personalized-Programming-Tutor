import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import ChatPanel from "../components/ChatPanel";
import TopicPicker from "../components/TopicPicker";
import TopicChip from "../components/TopicChip";
import InsightDrawer from "../components/InsightDrawer";
import RecommendationCard from "../components/RecommendationCard";
import { sendMessage, getSkillStates, getTopics, getRecommendation, createSession, askQuestion, getTopicIntro, submitFeedback } from "../api";
const STUDENT_ID = 1;
let introInFlight = false;

export default function ChatPage({
  messages, setMessages,
  selectedTopic, setSelectedTopic,
  lastTrace, setLastTrace,
  sessionId, setSessionId,
  onSessionCreated,
}) {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [skills, setSkills] = useState([]);
  const [topics, setTopics] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    getTopics().then(setTopics).catch(console.error);
    getRecommendation(STUDENT_ID).then(setRecommendation).catch(console.error);
    refreshSkills();
    if (location.state?.initialTopic) {
      handleSelectTopic(location.state.initialTopic);
    }
  }, [location.state]);

  const refreshSkills = () => {
    getSkillStates(STUDENT_ID).then(setSkills).catch(console.error);
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "student", text }]);
    setLoading(true);
    try {
      let activeSessionId = sessionId;
      if (!activeSessionId) {
        const session = await createSession(STUDENT_ID);
        activeSessionId = session.id;
        setSessionId(activeSessionId);
      }

      const res = await sendMessage(STUDENT_ID, selectedTopic || null, text, activeSessionId);
      const plannerFrame = res.agent_trace.find((f) => f.agent === "planner");
      setMessages((prev) => [
        ...prev,
        {
          role: "tutor",
          text: res.tutor_response,
          trace: res.agent_trace,
          plannerNote: plannerFrame ? `planner routed to ${plannerFrame.recommended_topic}` : null,
          interactionId: res.id,
          pKnowBefore: res.p_know_before,
          pKnowAfter: res.p_know_after,
        },
      ]);
      setLastTrace(res.agent_trace);
      refreshSkills();
      onSessionCreated?.();
    } catch (err) {
      setMessages((prev) => [...prev, { role: "tutor", text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    setLoading(true);
    try {
      let activeSessionId = sessionId;
      if (!activeSessionId) {
        const session = await createSession(STUDENT_ID);
        activeSessionId = session.id;
        setSessionId(activeSessionId);
      }

      const res = await askQuestion(STUDENT_ID, selectedTopic, activeSessionId);
      setMessages((prev) => [
        ...prev,
        { role: "tutor", text: res.question, isQuestion: true },
      ]);
      onSessionCreated?.();
    } catch (err) {
      setMessages((prev) => [...prev, { role: "tutor", text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };
  const handleSelectTopic = async (topicSlug) => {
    setSelectedTopic(topicSlug);

    if (messages.length > 0 || introInFlight) return;
    introInFlight = true;

    setLoading(true);
    try {
      let activeSessionId = sessionId;
      if (!activeSessionId) {
        const session = await createSession(STUDENT_ID);
        activeSessionId = session.id;
        setSessionId(activeSessionId);
      }

      const res = await getTopicIntro(STUDENT_ID, topicSlug, activeSessionId);
      setMessages((prev) => [
        ...prev,
        { role: "tutor", text: res.intro, isIntro: true },
      ]);
      onSessionCreated?.();
    } catch (err) {
      setMessages((prev) => [...prev, { role: "tutor", text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
      introInFlight = false;
    }
  };

  const handleChangeTopic = () => {
    setMessages([]);
    setSelectedTopic("");
    setLastTrace(null);
    setSessionId(null);
  };

  const handleFeedback = async (interactionId, reaction) => {
    // optimistic update, since this is a low-stakes, easily-retried action
    setMessages((prev) =>
      prev.map((m) =>
        m.interactionId === interactionId
          ? { ...m, feedback: m.feedback === reaction ? null : reaction }
          : m
      )
    );
    try {
      await submitFeedback(interactionId, reaction);
    } catch (err) {
      console.error("Failed to submit feedback:", err);
    }
  };

  const currentPKnow = skills.find((s) => s.topic_slug === selectedTopic)?.p_know;

  if (!selectedTopic) {
    return (
      <>
        <div className="mb-4">
          <RecommendationCard compact onSelectTopic={handleSelectTopic} />
        </div>
        <TopicPicker
          topics={topics}
          skills={skills}
          recommendation={recommendation}
          onSelect={handleSelectTopic}
        />
      </>
    );
  }

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <TopicChip topicSlug={selectedTopic} pKnow={currentPKnow} onChange={handleChangeTopic} />
        <div className="flex items-center gap-2">
          <button
            onClick={handleAskQuestion}
            disabled={loading}
            className="rounded-lg border border-pine/30 bg-pine/8 px-3 py-1.5 text-xs font-medium text-pine hover:bg-pine/12 disabled:opacity-40"
          >
            Check my understanding
          </button>
          <button
            onClick={() => setDrawerOpen(true)}
            className="flex items-center gap-1.5 rounded-lg border border-text/15 px-3 py-1.5 text-xs text-muted hover:text-text"
          >
            insight panel <span className="text-clay">›</span>
          </button>
        </div>
      </div>

      <div style={{ height: "64vh" }}>
        <ChatPanel messages={messages} onSend={handleSend} loading={loading} onAskQuestion={handleAskQuestion} onFeedback={handleFeedback} />
      </div>

      <InsightDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        skills={skills}
        lastTrace={lastTrace}
      />
    </>
  );
}