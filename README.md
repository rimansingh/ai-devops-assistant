# AI DevOps Assistant

An LLM-powered assistant for DevOps engineers. Paste error logs, Dockerfiles, Terraform plans, or ask anything DevOps-related — the agent picks the right tool and gives you practical, actionable answers.

Built with **FastAPI + LangChain + Groq (LLaMA 3.3)** on the backend and **Streamlit** on the frontend, with **Supabase** for conversation persistence.

---

## What it does

| Capability | How to use it |
|---|---|
| CI/CD error analysis | Paste a GitHub Actions / Jenkins failure log |
| Terraform plan review | Paste `terraform plan` output |
| Dockerfile review | Paste your Dockerfile |
| Runbook generation | Describe an incident or outage |
| Log analysis | Paste application or system logs |
| General DevOps Q&A | Just ask |

---

## Project structure

```
ai-devops-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app, routes
│   │   ├── agent.py       # LangChain agent + Groq LLM
│   │   ├── tools.py       # Agent tools (cicd, terraform, docker, etc.)
│   │   ├── models.py      # Pydantic request/response models
│   │   ├── database.py    # Supabase conversation persistence
│   │   └── __init__.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py             # Streamlit UI
│   ├── Dockerfile
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml
│       └── frontend-deploy.yml
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Getting started

### Prerequisites

- Docker + Docker Compose
- A [Groq API key](https://console.groq.com) (free)
- A [Supabase](https://supabase.com) project (free tier works)

### 1. Clone and configure

```bash
git clone https://github.com/your-username/ai-devops-assistant.git
cd ai-devops-assistant
cp .env.example .env
```

Edit `.env` with your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ENVIRONMENT=development
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/metrics` | Usage metrics |
| POST | `/chat` | Send a message to the agent |

### Chat request example

```bash
Invoke-RestMethod -Method POST -Uri http://localhost:8000/chat \
  -ContentType "application/json" \
  -Body '{"message": "Review this Dockerfile", "history": []}'
```

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.3 70B via Groq |
| Agent framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database | Supabase (PostgreSQL) |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Local development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

> On Python 3.13+ install frontend deps with `pip install --only-binary=:all: -r requirements.txt`

---

## Environment variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLaMA access |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key |
| `BACKEND_URL` | URL the frontend uses to reach the backend |
| `ENVIRONMENT` | `development` or `production` |
