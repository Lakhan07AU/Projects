# AI Interview Bot

A small web application that runs a live mock interview using the **Groq LLM API**.
The user picks a job role and difficulty, the AI asks interview questions one at a time,
scores each answer out of 100, gives feedback, and generates the next question.

## Features

- Choose from 15 job roles and 3 difficulty levels (Easy / Medium / Hard)
- AI generates one tailored interview question at a time
- Answers are scored 0–100 with strengths and improvement tips
- Skip a question if you get stuck
- Final summary with average score and an overall verdict
- Clean, responsive dark-mode UI

## Tech Stack

| Layer    | Technology                                              |
| -------- | ------------------------------------------------------- |
| Frontend | HTML5, CSS3, Vanilla JavaScript (no frameworks)         |
| Backend  | Python 3.14, Flask 3                                    |
| LLM API  | Groq (OpenAI-compatible `/v1/chat/completions` endpoint) |
| Model    | `llama-3.3-70b-versatile`                               |
| HTTP     | `requests` (backend) / `fetch` (frontend)               |

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Put your API key in the .env file (already done if you cloned this)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
TOTAL_QUESTIONS=5

# 4. Run the server
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## How It Works

1. `GET  /`            → serves the UI
2. `GET  /api/meta`    → returns the list of roles, difficulties and question count
3. `POST /api/start`   → creates a session, generates the first question
4. `POST /api/answer`  → evaluates the answer (score + feedback) and generates the next question

Each session keeps a small in-memory state (role, difficulty, question history).
After the final question the server returns an overall summary (average score + verdict).

## Project Structure

```
Aibot/
├── app.py               # Flask backend + Groq API calls
├── templates/
│   └── index.html       # UI markup (3 screens)
├── static/
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic (fetch calls)
├── requirements.txt
└── .env                 # API key + model config
```

## Notes

- The API key is read from `.env` — keep it secret, don't commit it to version control.
- The evaluation prompt asks the model to return strict JSON (`response_format: json_object`),
  which is parsed and validated on the server.
