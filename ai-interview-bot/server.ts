import express from "express";
import path from "path";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json({ limit: "5mb" }));

// Server-side secret key fallback from user injection
const GROQ_KEY = process.env.GROQ_API_KEY || "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";
const GEMINI_KEY = process.env.GEMINI_API_KEY;

// Initialize Gemini SDK if key exists
let geminiClient: GoogleGenAI | null = null;
if (GEMINI_KEY && GEMINI_KEY !== "MY_GEMINI_API_KEY") {
  try {
    geminiClient = new GoogleGenAI({ apiKey: GEMINI_KEY });
  } catch (e) {
    console.warn("Failed to initialize Gemini client:", e);
  }
}

/**
 * Universal LLM calling helper:
 * Prioritizes Groq (Llama 3.3 70B Versatile) for ultra-fast response times,
 * with graceful fallback to Gemini and structured recovery.
 */
async function callLLM(systemPrompt: string, userPrompt: string, jsonMode = true): Promise<string> {
  // Strategy 1: Try Groq with Llama 3.3 70B
  if (GROQ_KEY) {
    try {
      const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${GROQ_KEY}`,
        },
        body: JSON.stringify({
          model: "llama-3.3-70b-versatile",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt }
          ],
          temperature: 0.6,
          response_format: jsonMode ? { type: "json_object" } : undefined,
        }),
      });

      if (response.ok) {
        const data = (await response.json()) as any;
        const text = data?.choices?.[0]?.message?.content;
        if (text) return text.trim();
      } else {
        const errText = await response.text();
        console.warn("Groq API error response:", response.status, errText);
      }
    } catch (err) {
      console.warn("Error calling Groq API, attempting fallback:", err);
    }
  }

  // Strategy 2: Try Gemini if available
  if (geminiClient) {
    try {
      const response = await geminiClient.models.generateContent({
        model: "gemini-2.5-flash",
        contents: [
          { role: "user", parts: [{ text: `${systemPrompt}\n\n${userPrompt}` }] }
        ],
        config: {
          temperature: 0.6,
          responseMimeType: jsonMode ? "application/json" : undefined,
        }
      });
      if (response.text) return response.text.trim();
    } catch (err) {
      console.warn("Gemini API error:", err);
    }
  }

  throw new Error("No active LLM provider succeeded. Please ensure a valid GROQ_API_KEY or GEMINI_API_KEY is configured.");
}

// Clean JSON parser
function safeJsonParse<T>(raw: string, fallback: T): T {
  try {
    let clean = raw.trim();
    if (clean.startsWith("```json")) {
      clean = clean.replace(/^```json/, "").replace(/```$/, "").trim();
    } else if (clean.startsWith("```")) {
      clean = clean.replace(/^```/, "").replace(/```$/, "").trim();
    }
    return JSON.parse(clean) as T;
  } catch (err) {
    console.error("Failed to parse LLM JSON:", raw, err);
    return fallback;
  }
}

// Helper to construct persona details
function getPersonaInstruction(personaId: string): string {
  switch (personaId) {
    case "faang_strict":
      return "You are Alex Vance, a Principal Bar Raiser at a top-tier FAANG tech company. You are exacting, rigorous, and expect deep architectural clarity, edge case handling, performance awareness, and clear trade-off analysis. Provide direct, constructive, but high-standard feedback.";
    case "encouraging_coach":
      return "You are Jordan Reed, a Senior Engineering Mentor. You are encouraging, insightful, and pedagogical. Highlight what the candidate did well while clearly explaining how to elevate their answer to the next level.";
    case "startup_cto":
      return "You are Elena Rostova, a high-growth Series-B Startup CTO. You value speed, pragmatism, business context, architectural scalability without over-engineering, and strong ownership mindset.";
    case "behavioral_expert":
      return "You are Dr. Marcus Hill, a Senior Leadership & Talent Director. You evaluate responses using the STAR method (Situation, Task, Action, Result), focusing on ownership, team collaboration, leadership, and emotional intelligence.";
    default:
      return "You are an experienced Technical Hiring Manager and Senior Interviewer conducting a realistic job interview.";
  }
}

// API: Health check & provider status
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    activeProvider: GROQ_KEY ? "Groq (Llama 3.3 70B)" : GEMINI_KEY ? "Google Gemini" : "None",
    hasGroqKey: Boolean(GROQ_KEY),
    hasGeminiKey: Boolean(GEMINI_KEY),
    serverTime: new Date().toISOString(),
  });
});

// API: Speech-to-text fallback (raw audio bytes -> Groq Whisper)
// Used when the browser's built-in Web Speech service is unavailable (e.g.
// regional/network restrictions). Client sends the raw recorded blob.
app.post(
  "/api/speech/transcribe",
  express.raw({
    type: ["audio/webm", "audio/ogg", "audio/mp4", "audio/m4a", "audio/wav", "audio/mpeg", "audio/*", "application/octet-stream"],
    limit: "25mb",
  }),
  async (req, res) => {
    try {
      if (!GROQ_KEY) {
        return res.status(500).json({ error: "GROQ_API_KEY is not configured for speech transcription." });
      }

      const audio = req.body as Buffer;
      if (!audio || audio.length === 0) {
        return res.status(400).json({ error: "No audio received." });
      }

      const mimeType = (req.headers["content-type"] || "audio/webm").split(";")[0].trim();
      const ext = mimeType.includes("ogg")
        ? "ogg"
        : mimeType.includes("mp4") || mimeType.includes("m4a")
        ? "m4a"
        : mimeType.includes("wav")
        ? "wav"
        : mimeType.includes("mpeg")
        ? "mp3"
        : "webm";

      const form = new FormData();
      form.append("file", new Blob([audio], { type: mimeType }), `recording.${ext}`);
      form.append("model", "whisper-large-v3");
      form.append("language", "en");
      form.append("response_format", "json");

      const resp = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
        method: "POST",
        headers: { Authorization: `Bearer ${GROQ_KEY}` },
        body: form,
      });

      const data = (await resp.json()) as any;
      if (!resp.ok) {
        console.warn("Groq transcription error:", resp.status, data);
        return res.status(502).json({ error: data?.error?.message || "Speech transcription service failed." });
      }

      res.json({ text: data.text || "" });
    } catch (err: any) {
      console.error("Error in /api/speech/transcribe:", err);
      res.status(500).json({ error: err.message || "Failed to transcribe audio." });
    }
  }
);

// API: Start interview & generate first question
app.post("/api/interview/start", async (req, res) => {
  try {
    const { config } = req.body;
    if (!config) {
      return res.status(400).json({ error: "Missing interview configuration" });
    }

    const personaPrompt = getPersonaInstruction(config.interviewerPersona);
    const roleTitle = config.customRoleTitle || config.roleId || "Software Engineer";
    const seniority = config.seniority || "senior";
    const interviewType = config.interviewType || "mixed";
    const company = config.companyTarget ? `Target Company: ${config.companyTarget}` : "";

    const systemPrompt = `${personaPrompt}
You are beginning a live mock interview for the position: "${roleTitle}" (Seniority: ${seniority}).
Interview Focus: ${interviewType}.
${company}

Your task is to craft Question 1 for this candidate.
For Question 1:
- Start with a calibrated, thought-provoking question suitable for a ${seniority} ${roleTitle}.
- If technical/system design: focus on a foundational architecture or real-world problem.
- If behavioral: focus on a defining career project, conflict, or high-stakes challenge.
- If mixed: start with an insightful technical or domain design scenario.

Return ONLY valid JSON matching this exact structure:
{
  "questionNumber": 1,
  "question": "The interview question text",
  "category": "e.g. System Design | Concurrency | Frontend Architecture | Behavioral | Data Modeling",
  "difficulty": "Standard",
  "contextTip": "A brief hint or note on what the interviewer is looking for in a strong response"
}`;

    const userPrompt = `Generate Question 1 for a ${seniority} ${roleTitle} candidate in a ${interviewType} interview.`;

    const rawResponse = await callLLM(systemPrompt, userPrompt, true);
    const parsed = safeJsonParse(rawResponse, {
      questionNumber: 1,
      question: `Could you walk me through the architecture of the most complex system or feature you've designed as a ${seniority} ${roleTitle}, highlighting the key technical trade-offs you made?`,
      category: "Architecture & Core Concepts",
      difficulty: "Standard",
      contextTip: "Focus on scalability, data flow, failure modes, and why you chose specific technologies."
    });

    res.json({
      sessionId: "session_" + Date.now(),
      firstTurn: {
        ...parsed,
        questionNumber: 1
      }
    });
  } catch (err: any) {
    console.error("Error in /api/interview/start:", err);
    res.status(500).json({ error: err.message || "Failed to start interview" });
  }
});

// API: Evaluate answer and generate next progressive question
app.post("/api/interview/evaluate-and-next", async (req, res) => {
  try {
    const {
      config,
      currentQuestion,
      userAnswer,
      previousTurns = [],
      questionNumber,
      isLastQuestion
    } = req.body;

    if (!config || !currentQuestion || userAnswer === undefined) {
      return res.status(400).json({ error: "Missing required evaluation fields" });
    }

    const personaPrompt = getPersonaInstruction(config.interviewerPersona);
    const roleTitle = config.customRoleTitle || config.roleId;
    const seniority = config.seniority || "senior";
    const totalQuestions = config.totalQuestions || 5;

    const previousContext = previousTurns
      .map((t: any, i: number) => `Q${i + 1}: ${t.question}\nScore: ${t.evaluation?.score ?? 'N/A'}/100\nVerdict: ${t.evaluation?.verdict ?? 'N/A'}`)
      .join("\n\n");

    const systemPrompt = `${personaPrompt}
You are evaluating a candidate's answer for the role of "${roleTitle}" (Seniority: ${seniority}).
Total questions in interview: ${totalQuestions}. Current question number: ${questionNumber}.

The current question asked was:
"${currentQuestion.question}" (Category: ${currentQuestion.category}, Difficulty: ${currentQuestion.difficulty})

The candidate answered:
"${userAnswer}"

Previous Questions & Performance:
${previousContext || "None (this is question 1)"}

Your tasks:
1. Rigorously evaluate the candidate's answer.
   - Score (0 to 100).
   - Verdict: Pick one of ["Strong Hire", "Hire", "Leaning Hire", "Needs Improvement", "Did Not Meet Bar"].
   - Metrics breakdown (0 to 100 for technicalAccuracy, clarityAndStructure, depthAndRelevance, problemSolvingOrSTAR).
   - 2-3 specific strengths shown in their answer.
   - 2-3 concrete areas for improvement.
   - 2-3 specific missed key points, edge cases, or industry best practices.
   - An exemplary benchmark answer demonstrating how a top 1% ${seniority} ${roleTitle} would answer.
   - A short, realistic in-character spoken comment from you as the interviewer.

2. ${isLastQuestion ? "This was the final question of the interview. Do NOT generate a next question." : "Generate the NEXT question (Question " + (questionNumber + 1) + "). The next question should build naturally upon their previous answers or challenge them on a complementary skill area (e.g. deeper technical dive, trade-offs, scalability, or leadership)."}

Return ONLY valid JSON matching this schema:
{
  "evaluation": {
    "score": 85,
    "verdict": "Hire",
    "metrics": {
      "technicalAccuracy": 88,
      "clarityAndStructure": 82,
      "depthAndRelevance": 85,
      "problemSolvingOrSTAR": 80
    },
    "strengths": ["Clear explanation of...", "Good consideration of..."],
    "areasForImprovement": ["Could have addressed...", "Needs clearer quantification of..."],
    "missedKeyPoints": ["CAP theorem trade-offs under network partition", "Cache invalidation stampede mitigation"],
    "exemplaryAnswer": "A concise, masterfully structured 2-3 paragraph demonstration answer...",
    "interviewerComment": "Your natural persona comment to the candidate"
  }${!isLastQuestion ? `,
  "nextQuestion": {
    "questionNumber": ${questionNumber + 1},
    "question": "The next question text...",
    "category": "e.g. Distributed Caching | Failure Recovery | Trade-off Analysis",
    "difficulty": "Challenging",
    "contextTip": "Interviewer hint for candidate"
  }` : ""}
}`;

    const userPrompt = `Evaluate the candidate's answer to Question ${questionNumber} and ${isLastQuestion ? "finalize" : "generate Question " + (questionNumber + 1)}.`;

    const rawResponse = await callLLM(systemPrompt, userPrompt, true);
    const parsed = safeJsonParse(rawResponse, {
      evaluation: {
        score: 75,
        verdict: "Leaning Hire",
        metrics: {
          technicalAccuracy: 75,
          clarityAndStructure: 75,
          depthAndRelevance: 75,
          problemSolvingOrSTAR: 75
        },
        strengths: ["Addressed the core concept directly"],
        areasForImprovement: ["Provide deeper specifics and numerical benchmarks"],
        missedKeyPoints: ["Edge case and failure scenario handling"],
        exemplaryAnswer: "A high-level response would clearly articulate trade-offs, architecture patterns, and reliability considerations.",
        interviewerComment: "Good baseline intuition. Let's dig deeper into the next area."
      },
      nextQuestion: !isLastQuestion ? {
        questionNumber: questionNumber + 1,
        question: "How would you monitor and troubleshoot this system if latency spiked by 300% under high concurrent load?",
        category: "Observability & Performance",
        difficulty: "Challenging",
        contextTip: "Mention telemetry metrics (p95/p99), profiling tools, and triage steps."
      } : undefined
    });

    res.json(parsed);
  } catch (err: any) {
    console.error("Error in /api/interview/evaluate-and-next:", err);
    res.status(500).json({ error: err.message || "Failed to evaluate answer" });
  }
});

// API: Generate final comprehensive scorecard & study plan
app.post("/api/interview/generate-report", async (req, res) => {
  try {
    const { config, turns } = req.body;
    if (!config || !turns || !Array.isArray(turns)) {
      return res.status(400).json({ error: "Missing interview turns data" });
    }

    const personaPrompt = getPersonaInstruction(config.interviewerPersona);
    const roleTitle = config.customRoleTitle || config.roleId;
    const seniority = config.seniority || "senior";

    const transcript = turns.map((t: any, idx: number) => `
[QUESTION ${idx + 1}] (${t.category} - ${t.difficulty})
Question: ${t.question}
Candidate Answer: ${t.userAnswer || "No answer provided"}
Score: ${t.evaluation?.score ?? 0}/100 (Verdict: ${t.evaluation?.verdict ?? 'N/A'})
Interviewer Notes: ${t.evaluation?.interviewerComment ?? ''}
Strengths: ${t.evaluation?.strengths?.join(", ") ?? ''}
Areas to improve: ${t.evaluation?.areasForImprovement?.join(", ") ?? ''}
`).join("\n---");

    const systemPrompt = `${personaPrompt}
You have just concluded a full mock interview for the candidate applying for: "${roleTitle}" (Seniority: ${seniority}).

Complete interview transcript:
${transcript}

Analyze the candidate's holistic performance across all questions.
Provide a comprehensive executive hiring scorecard, including:
1. Overall score (0-100) and overall hiring verdict ("Strong Hire", "Hire", "Leaning Hire", "Needs Improvement").
2. Executive Summary Assessment.
3. Competency Breakdown across 4-5 core competencies (e.g. Domain Expertise, System Scalability, Communication & Clarity, Problem Solving & STAR, Edge Case Mastery).
4. Top 3-4 overall strengths.
5. Top 3-4 critical growth areas.
6. A personalized 4-week structured preparation roadmap to help the candidate achieve a "Strong Hire" at top tier companies.
7. Final Hiring Manager Debrief Notes.

Return ONLY valid JSON matching this schema:
{
  "overallScore": 82,
  "overallVerdict": "Hire",
  "summaryAssessment": "2-3 paragraphs of detailed, balanced assessment...",
  "competencyBreakdown": [
    { "category": "Domain & Technical Architecture", "score": 85, "summary": "Demonstrated strong grasp of..." },
    { "category": "Problem Solving & Analytical Rigor", "score": 80, "summary": "Systematic breakdown..." },
    { "category": "Communication & Structure", "score": 82, "summary": "Clear communication..." },
    { "category": "Edge Cases & Reliability", "score": 78, "summary": "Good initial coverage..." }
  ],
  "topStrengths": ["Strength 1...", "Strength 2...", "Strength 3..."],
  "topGrowthAreas": ["Growth area 1...", "Growth area 2...", "Growth area 3..."],
  "tailoredStudyPlan": [
    { "week": "Week 1", "focus": "Core Fundamentals & Distributed Caching", "actionItems": ["Read DDIA Chapter 3", "Practice rate limiting design"] },
    { "week": "Week 2", "focus": "System Scalability & Latency Budgets", "actionItems": ["Analyze p99 latency mitigation patterns", "Implement CQRS simulation"] },
    { "week": "Week 3", "focus": "Behavioral STAR & Leadership Frameworks", "actionItems": ["Draft 5 high-impact project stories with quantified metrics", "Practice conflict resolution narrative"] },
    { "week": "Week 4", "focus": "Full Mock Simulation & Timed Drills", "actionItems": ["Run 3 full-length timed mock rounds", "Refine trade-off articulation"] }
  ],
  "hiringManagerNotes": "A summary note from the hiring bar raiser regarding hireability and team placement recommendation."
}`;

    const userPrompt = `Generate the comprehensive final interview report and 4-week study plan for this ${seniority} ${roleTitle} mock interview.`;

    const rawResponse = await callLLM(systemPrompt, userPrompt, true);
    const parsed = safeJsonParse(rawResponse, {
      overallScore: 80,
      overallVerdict: "Hire",
      summaryAssessment: "The candidate demonstrated solid conceptual competence and structured thinking throughout the interview.",
      competencyBreakdown: [
        { category: "Technical Depth", score: 80, summary: "Solid grasp of core engineering principles." },
        { category: "Communication", score: 82, summary: "Communicated reasoning clearly and logically." },
        { category: "Problem Solving", score: 78, summary: "Methodical approach to requirement breakdowns." }
      ],
      topStrengths: ["Strong baseline technical intuition", "Structured response delivery"],
      topGrowthAreas: ["Deepen coverage of edge cases and concurrency safeguards", "Quantify project impact metrics"],
      tailoredStudyPlan: [
        { week: "Week 1", focus: "Architecture Deep Dive", actionItems: ["Study high-scale distributed systems patterns"] },
        { week: "Week 2", focus: "Mock Drills", actionItems: ["Practice timed articulation under 3 minutes per question"] }
      ],
      hiringManagerNotes: "Candidate meets the standard bar and with targeted refinement on distributed failure modes will perform at a strong hire level."
    });

    res.json({ report: parsed });
  } catch (err: any) {
    console.error("Error in /api/interview/generate-report:", err);
    res.status(500).json({ error: err.message || "Failed to generate report" });
  }
});

// Vite middleware setup
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`AI Interview Bot Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
