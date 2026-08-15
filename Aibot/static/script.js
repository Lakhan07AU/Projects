const $ = (id) => document.getElementById(id);

let sessionId = null;
let meta = { total: 5 };

const screens = {
  setup: $("screen-setup"),
  interview: $("screen-interview"),
  results: $("screen-results"),
};

function showScreen(name) {
  Object.values(screens).forEach((s) => s.classList.remove("active"));
  screens[name].classList.add("active");
  window.scrollTo(0, 0);
}

function setStatus(text, state = "online") {
  $("statusText").textContent = text;
  $("statusDot").className = "dot " + (state === "idle" ? "" : state);
}

function setError(el, msg) {
  el.textContent = msg || "";
}

async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

function renderScore(score) {
  const ring = $("scoreRing");
  ring.style.setProperty("--score", score);
  const color = score >= 70 ? "#00e08f" : score >= 45 ? "#feca57" : "#ff6b81";
  ring.style.background = `conic-gradient(${color} calc(${score} * 1%), rgba(255,255,255,0.08) 0)`;
  $("scoreText").textContent = score;
}

function renderLists(strengths, improvements) {
  const fill = (el, items) => {
    el.innerHTML = "";
    (items || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
    if (!items || items.length === 0) {
      const li = document.createElement("li");
      li.textContent = "—";
      el.appendChild(li);
    }
  };
  fill($("strengthsList"), strengths);
  fill($("improvementsList"), improvements);
}

function setAnswering(on) {
  $("submitBtn").disabled = on;
  $("skipBtn").disabled = on;
  $("answerInput").disabled = on;
  if (on) setStatus("Thinking…", "busy");
  else setStatus("Ready");
}

function showQuestion(question, number, total) {
  $("questionText").textContent = question;
  $("questionCount").textContent = `Question ${number} / ${total}`;
  $("sessionInfo").textContent = `${meta.role} · ${meta.difficulty}`;
  $("questionBlock").classList.remove("hidden");
  $("feedbackBlock").classList.add("hidden");
  $("answerInput").value = "";
  setError($("interviewError"));
  $("answerInput").focus();
  setAnswering(false);
}

function showFeedback(data) {
  $("questionBlock").classList.add("hidden");
  $("feedbackBlock").classList.remove("hidden");
  renderScore(data.score);
  $("feedbackText").textContent = data.feedback;
  renderLists(data.strengths, data.improvements);
  setStatus("Ready");
}

function showResults(summary) {
  $("finalScore").textContent = summary.average;
  $("verdictText").textContent = summary.verdict;
  $("verdictSub").textContent = summary.verdict_text;

  const box = $("breakdown");
  box.innerHTML = "";
  summary.history.forEach((h, i) => {
    const item = document.createElement("div");
    item.className = "break-item";
    const num = document.createElement("span");
    num.className = "break-num";
    num.textContent = `Q${i + 1}`;
    const q = document.createElement("span");
    q.className = "break-q";
    q.textContent = h.question;
    const score = document.createElement("span");
    score.className = "break-score" + (h.score < 50 ? " low" : "");
    score.textContent = h.score;
    item.append(num, q, score);
    box.appendChild(item);
  });

  showScreen("results");
  setStatus("Ready");
}

async function startInterview() {
  const role = $("roleSelect").value;
  const difficulty = $("difficultySelect").value;
  if (!role) {
    setError($("setupError"), "Please choose a job role.");
    return;
  }
  setError($("setupError"));
  $("startBtn").disabled = true;
  $("startBtn").textContent = "Preparing interview…";
  setStatus("Thinking…", "busy");

  try {
    const data = await api("/api/start", { role, difficulty });
    sessionId = data.session_id;
    meta.role = role;
    meta.difficulty = difficulty;
    showScreen("interview");
    showQuestion(data.question, data.question_number, data.total);
  } catch (err) {
    setError($("setupError"), err.message);
    setStatus("Ready");
  } finally {
    $("startBtn").disabled = false;
    $("startBtn").textContent = "Start Interview";
  }
}

async function submitAnswer() {
  const answer = $("answerInput").value.trim();
  if (!answer) {
    setError($("interviewError"), "Please type an answer first.");
    return;
  }
  setError($("interviewError"));
  setAnswering(true);

  try {
    const data = await api("/api/answer", { session_id: sessionId, answer });
    if (data.done) {
      showResults(data.summary);
    } else {
      showFeedback(data);
      $("nextBtn").onclick = () => showQuestion(data.next_question, data.question_number, data.total);
    }
  } catch (err) {
    setError($("interviewError"), err.message);
    setAnswering(false);
  }
}

async function skipQuestion() {
  if (!confirm("Skip this question? It will be counted as an empty answer.")) return;
  $("answerInput").value = "I don't know.";
  submitAnswer();
}

function resetApp() {
  sessionId = null;
  $("roleSelect").value = "";
  $("difficultySelect").value = "Medium";
  showScreen("setup");
  setStatus("Ready");
}

async function init() {
  try {
    const data = await api("/api/meta");
    meta.total = data.total_questions;
    const select = $("roleSelect");
    select.innerHTML = '<option value="">Select a job role…</option>' +
      data.roles.map((r) => `<option value="${r}">${r}</option>`).join("");
    $("totalHint").textContent =
      `The interviewer will ask ${data.total_questions} questions and score each answer out of 100.`;
  } catch (err) {
    setError($("setupError"), err.message);
    setStatus("Offline", "idle");
  }
}

$("startBtn").addEventListener("click", startInterview);
$("submitBtn").addEventListener("click", submitAnswer);
$("skipBtn").addEventListener("click", skipQuestion);
$("restartBtn").addEventListener("click", resetApp);
$("answerInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!$("submitBtn").disabled) submitAnswer();
  }
});

init();
