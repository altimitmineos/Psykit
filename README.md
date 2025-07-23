# 🧠 Psykit – Empathetic Mental Health Chatbot

**Psykit** is an AI-powered chatbot designed to provide emotional support and empathy for users experiencing stress, anxiety, or life challenges. Built using **FastAPI**, **SQLite**, and a locally fine-tuned **GGUF-based LLM**, it offers real-time, bilingual conversation in **Bahasa Indonesia** and **English**, with context-aware responses and a gentle, supportive tone.

---

## 🚀 Features

- 🔐 **User Authentication** (signup & login with hashed passwords)
- 💬 **Personalized Chat History** (stored per user, using SQLite)
- 🧠 **Local LLM Inference** with `llama-cpp-python`
- 🗣️ **Bilingual Responses** (auto-detects Bahasa Indonesia or English)
- 🧘 **Empathetic Psychology Assistant** (Alpaca prompt format)
- 🌐 **Deployed on a VPS** using Nginx + Gunicorn + systemd

---

## 🛠️ Tech Stack

| Layer         | Tools                              |
|--------------|-------------------------------------|
| 🧠 AI Model   | GGUF fine-tuned LLM (Alpaca-style)  |
| 🐍 Backend    | FastAPI, SQLAlchemy, SQLite         |
| 🌐 Frontend   | HTML, CSS (Jinja2 Templates)        |
| 🔒 Auth       | bcrypt, SessionMiddleware           |
| 📦 LLM Engine | llama-cpp-python                    |
| 🚀 Deploy     | Gunicorn, UvicornWorker, Nginx      |

---

## ⚙️ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/psykit.git
cd psykit
