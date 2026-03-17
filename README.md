# AI DevOps Assistant 🤖

> An LLM-powered assistant that helps DevOps engineers debug pipelines, review infrastructure code, and generate incident runbooks — in plain English.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Spaces-orange?style=flat-square)](https://rimandeep-ai-devops-frontend.hf.space/)

**🚀 [Try it live → rimandeep-ai-devops-frontend.hf.space](https://rimandeep-ai-devops-frontend.hf.space/)**

---

## What it does

Paste any of the following directly into the chat and get an actionable, plain-English response:

| Input | What you get |
|---|---|
| A GitHub Actions / Jenkins failure log | Root cause + exact fix commands |
| `terraform plan` output | Plain-English summary of changes + risk flags |
| A Dockerfile | Security issues, best-practice violations, fixed version |
| An incident description | Structured runbook with triage steps and rollback plan |
| Application / system logs | Error patterns, timeline, recommended actions |
| Any DevOps question | Direct answer from a model trained on engineering context |

---

## Architecture

```
GitHub (rimansingh/ai-devops-assistant)
    │
    push to main
    ├── backend/**  →  backend-deploy.yml  →  git push → HF Docker Space
    └── frontend/** →  frontend-deploy.yml →  git push → HF Streamlit Space
                                                │                    │
                                         ┌──────────────────────────────────┐
                                         │        HuggingFace Spaces        │
                                         │  ┌─────────────────┐             │
                          User ──────────┼─►│ Streamlit Space │             │
                                         │  │   (frontend)    │             │
                                         │  └────────┬────────┘             │
                                         │  POST /chat│  JSON response       │
                                         │  ┌─────────▼───────┐             │
                                         │  │  Docker Space   │             │
                                         │  │ FastAPI+LangChain│            │
                                         │  └──┬──────┬───────┘             │
                                         └─────┼──────┼─────────────────────┘
                                               │      │
                                    ┌──────────┘      └──────────────┐
                                    ▼                                 ▼
                               Supabase                          Groq API
                           (conversation history)            (LLaMA 3.3 70B)

                    cron-job.org ──── pings /health every 10 min ────►
```

**Why this stack?**

| Component | Choice | Why |
|---|---|---|
| LLM | LLaMA 3.3 70B via Groq | Free tier, ~300 token/s, strong on code |
| Agent framework | LangChain | Tool-calling abstraction, conversation memory |
| Backend | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation |
| Frontend | Streamlit | Rapid UI, no JS needed, free hosting on HuggingFace |
| Database | Supabase | Managed Postgres, free tier, conversation persistence |
| Container | Docker | Reproducible builds, same image local and production |
| CI/CD | GitHub Actions | Native GitHub, free for public repos |
| Hosting | HuggingFace Spaces | Free Docker + Streamlit hosting |
| Keepalive | cron-job.org | Free pings every 10 min to prevent HF sleep |

---

## The 5 Agent Tools

The LangChain agent automatically selects the right tool based on what you paste or ask:

```
explain_cicd_error      → GitHub Actions / Jenkins error logs
explain_terraform_plan  → terraform plan output
review_dockerfile       → Dockerfile content
generate_runbook        → incident / outage descriptions
analyse_logs            → application or system log snippets
```

If none of the tools are needed (e.g. a general question), the agent answers directly without calling any tool.

---

## Project Structure

```
ai-devops-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app — routes, CORS, structured logging
│   │   ├── agent.py       # LangChain agent executor + Groq LLM setup
│   │   ├── tools.py       # 5 agent tools (cicd, terraform, docker, runbook, logs)
│   │   ├── models.py      # Pydantic request/response models
│   │   ├── database.py    # Supabase client — save conversations, fetch metrics
│   │   └── __init__.py
│   ├── Dockerfile         # Non-root user, health check, slim base image
│   └── requirements.txt
├── frontend/
│   ├── app.py             # Streamlit UI — chat, sidebar metrics, health status
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml   # Syncs backend/ to HF Docker Space on push
│       └── frontend-deploy.yml  # Syncs frontend/ to HF Streamlit Space on push
├── docker-compose.yml     # Local development — both services wired together
├── .env.example           # Template — copy to .env and fill in keys
└── .gitignore
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Live usage stats — total requests, avg response time, tools used |
| `POST` | `/chat` | Send a message, get an agent response |

**`POST /chat` — example request:**
```json
{
  "message": "Why is my GitHub Actions workflow failing?",
  "conversation_id": "abc-123",
  "history": [
    { "role": "user",      "content": "Previous message" },
    { "role": "assistant", "content": "Previous reply"   }
  ]
}
```

**Response:**
```json
{
  "reply": "The failure is caused by...",
  "conversation_id": "abc-123",
  "tool_used": "explain_cicd_error"
}
```

---

## Local Development

**Prerequisites:** Python 3.11+, Docker, Git

```bash
# 1. Clone the repo
git clone https://github.com/rimansingh/ai-devops-assistant.git
cd ai-devops-assistant

# 2. Set up environment variables
cp .env.example .env
# Edit .env and fill in: GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY

# 3. Start both services with Docker Compose
docker compose up --build

# Backend:  http://localhost:8000
# Frontend: http://localhost:8501
```

**Test the backend directly:**
```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a Dockerfile?", "history": []}'
```

> **Python 3.13+ note:** Install frontend deps with `pip install --only-binary=:all: -r requirements.txt`

---

## Environment Variables

| Variable | Description | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | LLM API key | [console.groq.com](https://console.groq.com) |
| `SUPABASE_URL` | Supabase project URL | Supabase dashboard → Project Settings |
| `SUPABASE_KEY` | Supabase anon key | Supabase dashboard → Project Settings |
| `BACKEND_URL` | URL the frontend calls | Your HF backend Space URL |
| `ENVIRONMENT` | `development` or `production` | Set manually |

Never commit `.env` — it is in `.gitignore`. Use GitHub Actions secrets for CI/CD and HuggingFace Space secrets for production.

---

## CI/CD Pipeline

Every push to `main` triggers automated workflows:

**Backend (`backend-deploy.yml`):**
```
push to main (backend/** changed)
  └── git push backend/ → HuggingFace Docker Space → HF rebuilds container
```

**Frontend (`frontend-deploy.yml`):**
```
push to main (frontend/** changed)
  └── git push frontend/ → HuggingFace Streamlit Space → HF redeploys UI
```

Secrets (`HF_TOKEN`, `HF_BACKEND_SPACE_ID`, `HF_FRONTEND_SPACE_ID`) are stored as GitHub Actions secrets — never in code.

---

## Monitoring

| Monitor | Details |
|---|---|
| Backend keepalive | cron-job.org pings `/health` every 10 min to prevent HF sleep |
| Metrics | `/metrics` endpoint — live request count + avg response time |

The backend emits structured JSON logs on every request:
```json
{
  "level": "INFO",
  "message": "Agent response",
  "response_time_ms": 1840,
  "tool_used": "explain_cicd_error"
}
```

---

## Roadmap

- [ ] Add unit tests for all agent tools
- [ ] Slack bot integration
- [ ] Support for Kubernetes manifests
- [ ] RAG over user's own runbook documentation

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)

---

## Author

**Rimandeep Singh** — DevOps / Cloud / AI Engineer  
[LinkedIn](https://www.linkedin.com/in/rimandeep-singh/) · [GitHub](https://github.com/rimansingh) · [Portfolio](https://portfolio-website-3qw.pages.dev/)
