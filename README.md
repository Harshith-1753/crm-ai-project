# 🤖 AI-Powered CRM System (LangGraph + FastAPI + React)

## 📌 Overview

This project is an AI-powered Customer Relationship Management (CRM) system that enables intelligent interaction logging using natural language.

It integrates **LangGraph workflows**, **Groq LLM**, and a **React frontend** to automate data entry, summarization, and next-step suggestions.

---

## 🚀 Features

* 🧠 AI Chat-based Interaction Logging
* 📋 Auto-fill CRM Forms using LLM
* ✏️ Edit & Update Interactions
* 📊 Dashboard Analytics
* 🕓 Interaction History Tracking
* 📄 CSV Export
* 🤖 AI Summarization
* 🔮 AI Suggested Next Actions
* 🔗 LangGraph Workflow Integration

---

## 🏗️ Tech Stack

**Frontend:**

* React.js
* Axios
* CSS

**Backend:**

* FastAPI
* LangGraph
* Groq LLM (LLaMA 3.3)
* SQLite

---

## 🧠 Architecture

Frontend → FastAPI → LangGraph → Tools → LLM + Database

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/crm-ai-project.git
cd crm-ai-project
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run server:

```bash
uvicorn main:app --reload
```

---

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## 🎥 Demo Flow

* Log interaction via chat
* AI auto-fills form
* Save → appears in history
* Edit interaction
* Ask “summarize” or “suggest next step”

---

## 📸 Screenshot

(Add your UI screenshot here)

---

## 📌 Future Improvements

* Authentication system
* Deployment (Render / Vercel)
* Role-based access
* Real-time notifications

---

## 👨‍💻 Author

Harshith Rajellipeta