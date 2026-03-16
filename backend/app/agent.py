import os
import time
import logging
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from app.tools import (
    explain_cicd_error,
    explain_terraform_plan,
    review_dockerfile,
    generate_runbook,
    analyse_logs,
)

logger = logging.getLogger(__name__)

# All tools the agent can use
TOOLS = [
    explain_cicd_error,
    explain_terraform_plan,
    review_dockerfile,
    generate_runbook,
    analyse_logs,
]

SYSTEM_PROMPT = """You are an expert AI DevOps Assistant with deep knowledge of:
- CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- Infrastructure as Code (Terraform, Ansible)
- Containers and orchestration (Docker, Kubernetes)
- Cloud platforms (AWS, GCP, Azure)
- Site reliability engineering (SRE) practices
- Linux systems and networking
- Application logs and observability

You help engineers understand and solve DevOps problems clearly and practically.

You have access to specialised tools:
- explain_cicd_error: for analysing pipeline failures and error logs
- explain_terraform_plan: for interpreting terraform plan output
- review_dockerfile: for reviewing Dockerfiles for issues
- generate_runbook: for creating incident response runbooks
- analyse_logs: for analysing application/system logs

IMPORTANT RULES:
1. Always use the appropriate tool when the user provides relevant input
   (error logs, Dockerfiles, terraform plans, log snippets)
2. If no tool is needed, answer directly from your knowledge
3. Be specific and practical — give exact commands and fixes, not vague advice
4. Format your responses with clear sections and use markdown
5. If you are unsure, say so clearly rather than guessing
"""


def build_agent() -> AgentExecutor:
    """Build and return the LangChain agent executor."""
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0.1,      # Low temperature = more consistent, factual answers
        max_tokens=4096,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,           # Logs tool calls — useful for debugging
        max_iterations=3,       # Prevent infinite loops
        handle_parsing_errors=True,
    )


def convert_history(history: list) -> list:
    """Convert API message history format to LangChain message objects."""
    messages = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    return messages


def run_agent(message: str, history: list) -> dict:
    """
    Run the agent with a message and conversation history.
    Returns the response text and which tool was used (if any).
    """
    start_time = time.time()

    agent_executor = build_agent()
    chat_history = convert_history(history)

    try:
        result = agent_executor.invoke({
            "input": message,
            "chat_history": chat_history,
        })

        elapsed_ms = round((time.time() - start_time) * 1000)

        # Detect which tool was used from the agent's intermediate steps
        tool_used = None
        if result.get("intermediate_steps"):
            last_step = result["intermediate_steps"][-1]
            if hasattr(last_step[0], "tool"):
                tool_used = last_step[0].tool

        logger.info(
            "Agent response",
            extra={
                "response_time_ms": elapsed_ms,
                "tool_used": tool_used,
                "success": True,
            }
        )

        return {
            "reply": result["output"],
            "tool_used": tool_used,
            "response_time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = round((time.time() - start_time) * 1000)
        logger.error(f"Agent error: {e}", extra={"response_time_ms": elapsed_ms})
        raise