import json
import os
import re
import uuid

import requests
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


load_env()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

TOTAL_QUESTIONS = int(os.environ.get("TOTAL_QUESTIONS", "5"))

app = Flask(__name__)
sessions = {}

ROLES = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Product Manager",
    "UI/UX Designer",
    "Project Manager",
    "QA / Test Engineer",
    "Mobile App Developer (Android)",
    "Mobile App Developer (iOS)",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]

INTERVIEWER_SYSTEM = (
    "You are a professional hiring manager conducting a structured job interview. "
    "You are firm but encouraging. Ask exactly ONE interview question at a time. "
    "Do not write 'Question 1:' or any numbering, do not write any preamble, do not "
    "answer the question yourself. Just output the single question."
)


def call_groq(messages, json_mode=False):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Model did not return valid JSON")


def new_session(role, difficulty):
    session_id = uuid.uuid4().hex[:16]
    sessions[session_id] = {
        "role": role,
        "difficulty": difficulty,
        "number": 0,
        "history": [],
        "current": None,
    }
    return session_id


def generate_question(state):
    role = state["role"]
    difficulty = state["difficulty"]
    number = state["number"]

    history = state["history"]
    if history:
        previous = "\n".join(
            f'Q{i}. {h["question"]}\nA{i}. {h["answer"]}' for i, h in enumerate(history, 1)
        )
        context = (
            f"The candidate has already answered these questions in this interview:\n\n"
            f"{previous}\n\n"
            "Ask the NEXT question. Do not repeat any earlier question."
        )
    else:
        context = "This is the first question of the interview."

    messages = [
        {"role": "system", "content": INTERVIEWER_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Job role: {role}\n"
                f"Difficulty level: {difficulty}\n"
                f"Question number: {number + 1} of {TOTAL_QUESTIONS}\n\n"
                f"{context}\n\n"
                "Generate one relevant, specific interview question."
            ),
        },
    ]
    return call_groq(messages)


def evaluate_answer(state, question, answer):
    role = state["role"]
    difficulty = state["difficulty"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert interviewer who evaluates candidate answers. "
                'Always respond with valid JSON only, using this exact schema:\n'
                '{"score": <integer 0-100>, '
                '"feedback": "<short paragraph of honest feedback>", '
                '"strengths": ["<strength 1>", "<strength 2>"], '
                '"improvements": ["<improvement 1>", "<improvement 2>"]}'
            ),
        },
        {
            "role": "user",
            "content": (
                f"Job role: {role}\n"
                f"Difficulty level: {difficulty}\n\n"
                f"Question: {question}\n\n"
                f"Candidate's answer:\n{answer}\n\n"
                "Evaluate the answer fairly. Return the JSON only."
            ),
        },
    ]
    raw = call_groq(messages, json_mode=True)
    data = extract_json(raw)
    return {
        "score": max(0, min(100, int(data.get("score", 50)))),
        "feedback": str(data.get("feedback", "")).strip(),
        "strengths": data.get("strengths", []),
        "improvements": data.get("improvements", []),
    }


def build_summary(session_id, state):
    history = state["history"]
    total = len(history)
    if total == 0:
        return None
    average = round(sum(h["score"] for h in history) / total)
    verdict = "Excellent! You would be a strong hire." if average >= 80 else (
        "Good performance, but there is room for improvement."
        if average >= 60 else
        "Below average. Practice the fundamentals and try again."
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a career coach. Write a short, honest final verdict "
                "for a mock interview candidate. 2-3 sentences maximum."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Job role: {state['role']}\n"
                f"Average score: {average}/100\n"
                f"Scores per question: {[h['score'] for h in history]}\n\n"
                "Write the final verdict."
            ),
        },
    ]
    verdict_text = call_groq(messages)

    return {
        "average": average,
        "verdict": verdict,
        "verdict_text": verdict_text,
        "history": history,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/meta")
def meta():
    return jsonify(roles=ROLES, difficulties=DIFFICULTIES, total_questions=TOTAL_QUESTIONS)


@app.route("/api/start", methods=["POST"])
def start():
    body = request.get_json(silent=True) or {}
    role = body.get("role", "").strip()
    difficulty = body.get("difficulty", "").strip()

    if role not in ROLES:
        return jsonify(error="Please choose a valid job role."), 400
    if difficulty not in DIFFICULTIES:
        return jsonify(error="Please choose a valid difficulty."), 400

    session_id = new_session(role, difficulty)
    state = sessions[session_id]
    try:
        question = generate_question(state)
    except Exception as exc:
        return jsonify(error=f"Could not generate question: {exc}"), 500

    state["number"] = 1
    state["current"] = question

    return jsonify(
        session_id=session_id,
        question=question,
        question_number=1,
        total=TOTAL_QUESTIONS,
    )


@app.route("/api/answer", methods=["POST"])
def answer():
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id", "")
    answer_text = body.get("answer", "").strip()

    state = sessions.get(session_id)
    if not state:
        return jsonify(error="Session not found. Please restart the interview."), 404
    if not answer_text:
        return jsonify(error="Please type an answer first."), 400

    question = state["current"]

    try:
        result = evaluate_answer(state, question, answer_text)
    except Exception as exc:
        return jsonify(error=f"Could not evaluate answer: {exc}"), 500

    state["history"].append({
        "question": question,
        "answer": answer_text,
        "score": result["score"],
        "feedback": result["feedback"],
        "strengths": result["strengths"],
        "improvements": result["improvements"],
    })

    if state["number"] >= TOTAL_QUESTIONS:
        summary = build_summary(session_id, state)
        sessions.pop(session_id, None)
        return jsonify(
            done=True,
            score=result["score"],
            feedback=result["feedback"],
            strengths=result["strengths"],
            improvements=result["improvements"],
            summary=summary,
        )

    try:
        next_question = generate_question(state)
    except Exception as exc:
        return jsonify(error=f"Could not generate next question: {exc}"), 500

    state["number"] += 1
    state["current"] = next_question

    return jsonify(
        done=False,
        score=result["score"],
        feedback=result["feedback"],
        strengths=result["strengths"],
        improvements=result["improvements"],
        next_question=next_question,
        question_number=state["number"],
        total=TOTAL_QUESTIONS,
    )


if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("WARNING: GROQ_API_KEY not set. Create a .env file with GROQ_API_KEY=...")
    app.run(debug=True, host="127.0.0.1", port=5000)
