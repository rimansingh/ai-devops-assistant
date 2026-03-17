# AI DevOps Assistant

An LLM-powered assistant for DevOps engineers. Paste error logs, Dockerfiles, Terraform plans, or ask anything DevOps-related — the agent picks the right tool and gives you practical, actionable answers.

Built with **FastAPI + LangChain + Groq (LLaMA 3.3)** on the backend and **Streamlit** on the frontend, with **Supabase** for conversation persistence. Hosted on **HuggingFace Spaces** with CI/CD via **GitHub Actions**.

🚀 **Live app:** [huggingface.co/spaces/rimandeep/ai-devops-assistant](https://huggingface.co/spaces/rimandeep/ai-devops-assistant)

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

## How it's built

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.3 70B via Groq |
| Agent framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database | Supabase (PostgreSQL) |
| Containerisation | Docker |
| CI/CD | GitHub Actions |
| Hosting | HuggingFace Spaces |

---

## How it's deployed

The app runs as two HuggingFace Spaces:

- **Backend** — Docker Space running FastAPI on port 7860
- **Frontend** — Streamlit Space serving the chat UI

Every push to the `main` branch on GitHub automatically syncs the relevant folder to its HuggingFace Space via GitHub Actions workflows. No manual deployment needed.

```
Push to main
  ├── backend/** changed → GitHub Action → HF Docker Space (FastAPI)
  └── frontend/** changed → GitHub Action → HF Streamlit Space (UI)
```

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
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml   # Syncs backend/ to HF on push
│       └── frontend-deploy.yml  # Syncs frontend/ to HF on push
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/metrics` | Usage metrics |
| POST | `/chat` | Send a message to the agent |

---

## Local development

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

Copy `.env.example` to `.env` and fill in your own API keys before running locally.

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
