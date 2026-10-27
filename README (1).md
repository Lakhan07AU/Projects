<div align="center">

# ✨ Lakhan's Project Lab

### Building ideas into useful products — one project at a time.

A collection of my work across **AI/ML, healthcare technology, computer vision, data analytics, and web development**.

[Explore Projects](#-featured-projects) · [Tech Stack](#-technology-toolbox) · [Run Locally](#-getting-started) · [Connect](#-connect)

[![GitHub](https://img.shields.io/badge/GitHub-Lakhan07AU-181717?style=for-the-badge&logo=github)](https://github.com/Lakhan07AU)
[![Projects](https://img.shields.io/badge/Repository-Projects-2563eb?style=for-the-badge&logo=github)](https://github.com/Lakhan07AU/Projects)

</div>

---

## 🧭 Explore this repository

| Project | What it explores | Main area |
|---|---|---|
| 🩺 [HealthSphere](#-1-healthsphere) | Personal health records, family history, report processing, and preventive-care insights | Healthcare Tech · Full Stack |
| 🛣️ [RoadGuard](#-2-roadguard) | Computer-vision-based road and pothole monitoring | Computer Vision · AI |
| ❤️ [Cardiovascular Disease Analysis](#-3-cardiovascular-disease-data-analysis) | Data cleaning, risk-factor analysis, statistics, SQL, and machine learning | Data Analytics · ML |
| 🎙️ [AI Interview Bot](#-4-ai-interview-bot) | Practice interviews with AI-generated questions and answer feedback | Generative AI · Web App |
| 🤖 [AI Studio Interview App](#-5-ai-studio-interview-app) | A web app created with Google AI Studio | Generative AI · Web Development |
| 🎂 [Birthday Website](#-6-birthday-website) | A personal website project | Frontend Development |

> **Tip:** Select any project title to open its source folder. Each project may have its own setup instructions and dependencies.

---

## 🚀 Featured Projects

<a id="-1-healthsphere"></a>
### 🩺 1. HealthSphere — Personal Health Record Platform

**The idea:** Keep health information easier to organize and understand, instead of scattered across reports and notes.

- 🧬 Family health history and relative-level condition tracking
- 📄 Upload medical reports and extract values from PDFs or images
- 📈 Track health metrics and review trends over time
- 💡 Rule-based preventive-care insights linked to source rules
- 🔐 Privacy controls, data export, and account deletion features

**Technology:** Next.js, TypeScript, FastAPI, Python, PostgreSQL/SQLite, Redis, Celery.

[**Open HealthSphere →**](https://github.com/Lakhan07AU/Projects/tree/main/HealthSphere)

<details>
<summary>🛠️ Local setup</summary>

Follow the detailed instructions in the [HealthSphere README](https://github.com/Lakhan07AU/Projects/tree/main/HealthSphere). The project supports local development with SQLite and an inline task queue, as well as a Docker-based setup.

> HealthSphere is an educational project, not a medical device. Its insights do not replace advice from a qualified healthcare professional.

</details>

---

<a id="-2-roadguard"></a>
### 🛣️ 2. RoadGuard — Road Condition Monitoring

**The idea:** Explore how computer vision can help identify road damage, including potholes, and support road-condition reporting.

- 🕳️ Pothole-detection project
- 🌐 Web interface and backend components
- 🔎 Designed around applying computer vision to a real-world road-safety problem

**Technology:** See the project folder for the current frontend, backend, and model configuration.

[**Open RoadGuard →**](https://github.com/Lakhan07AU/Projects/tree/main/RoadGuard)

---

<a id="-3-cardiovascular-disease-data-analysis"></a>
### ❤️ 3. Cardiovascular Disease Data Analysis

**The idea:** Investigate cardiovascular disease risk factors using a structured analytics workflow.

- 🧹 Data-quality checks and cleaning of a 70,000-record dataset
- 📊 Exploratory analysis and visualizations
- 🧪 Statistical analysis and hypothesis testing
- 🗃️ SQL analysis and feature engineering
- 🤖 Machine-learning model comparison and feature-importance analysis

**Technology:** Python, Pandas, Jupyter Notebook, SQL, machine learning, and Power BI dashboard planning.

[**Open analysis project →**](https://github.com/Lakhan07AU/Projects/tree/main/Cardiovascular-Disease-Data-Analysis)

---

<a id="-4-ai-interview-bot"></a>
### 🎙️ 4. AI Interview Bot

**The idea:** Give users a way to practice mock interviews and receive structured feedback on their answers.

- 🎯 Choose from job roles and difficulty levels
- 💬 Receive AI-generated questions one at a time
- 📝 Get a score, strengths, and improvement suggestions
- 📋 Review a final performance summary

**Technology:** Python, Flask, HTML, CSS, JavaScript, and the Groq API using `llama-3.3-70b-versatile` as documented in the project.

[**Open AI Interview Bot →**](https://github.com/Lakhan07AU/Projects/tree/main/Aibot)

<details>
<summary>▶️ Run locally</summary>

```bash
cd Aibot
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Install dependencies:
pip install -r requirements.txt
```

Configure your own Groq API key in a local `.env` file, then run:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser. **Never publish API keys or secrets.**

</details>

---

<a id="-5-ai-studio-interview-app"></a>
### 🤖 5. AI Studio Interview App

A separate web application scaffolded with Google AI Studio.

[**Open AI Studio app source →**](https://github.com/Lakhan07AU/Projects/tree/main/ai-interview-bot) · [Open in Google AI Studio](https://ai.studio/apps/959501d7-d08b-42a1-ab73-aee6c9d7ebaa)

<details>
<summary>▶️ Run locally</summary>

```bash
cd ai-interview-bot
npm install
```

Set `GEMINI_API_KEY` in a local `.env.local` file, then start the development server:

```bash
npm run dev
```

Follow the app's own README for current configuration details.

</details>

---

<a id="-6-birthday-website"></a>
### 🎂 6. Birthday Website

A personal website project exploring creative web presentation and frontend development.

[**Open Birthday Website →**](https://github.com/Lakhan07AU/Projects/tree/main/birthday-website%20(1))

---

## 🧰 Technology Toolbox

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)

</div>

*Technologies vary by project. Check each project's source and documentation for the exact implementation.*

---

## 🧪 Getting Started

This repository contains multiple independent projects, so there is **no single install command** for everything.

1. Browse the project list above.
2. Open the project's folder and read its README.
3. Install the dependencies for that project only.
4. Add required API keys to local environment files; do not commit secrets.
5. Follow the project-specific run and test instructions.

## 🗺️ What's next?

- Improve project documentation and add demo screenshots where available.
- Keep setup steps and dependencies up to date.
- Add public demos when they are ready.
- Continue improving testing, reliability, and usability.

## 🤝 Feedback & Collaboration

Found something interesting or have a suggestion? Open an issue in the repository or connect with me on GitHub.

<div align="center">

### 👋 Let's build something useful.

[![GitHub Profile](https://img.shields.io/badge/Follow%20my%20work-Lakhan07AU-181717?style=for-the-badge&logo=github)](https://github.com/Lakhan07AU)

**Made with curiosity, code, and continuous learning.**

</div>
