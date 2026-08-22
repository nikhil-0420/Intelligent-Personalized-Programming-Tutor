const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function sendMessage(studentId, topicSlug, message, sessionId) {
  const res = await fetch(`${BASE_URL}/tutor/interact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      topic_slug: topicSlug,
      message,
      session_id: sessionId,
    }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function getSkillStates(studentId) {
  const res = await fetch(`${BASE_URL}/students/${studentId}/skills`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function getTopics() {
  const res = await fetch(`${BASE_URL}/topics`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function getRecommendation(studentId) {
  const res = await fetch(`${BASE_URL}/students/${studentId}/recommend-topic`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function createSession(studentId) {
  const res = await fetch(`${BASE_URL}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function listSessions(studentId) {
  const res = await fetch(`${BASE_URL}/students/${studentId}/sessions`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function getSessionMessages(sessionId) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function askQuestion(studentId, topicSlug, sessionId) {
  const res = await fetch(`${BASE_URL}/tutor/ask-question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      topic_slug: topicSlug,
      session_id: sessionId,
    }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function getTopicIntro(studentId, topicSlug, sessionId) {
  const res = await fetch(`${BASE_URL}/tutor/topic-intro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      topic_slug: topicSlug,
      session_id: sessionId,
    }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function submitFeedback(interactionId, feedback) {
  const res = await fetch(`${BASE_URL}/interactions/${interactionId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}