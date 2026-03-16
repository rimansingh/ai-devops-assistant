from langchain_core.tools import tool


@tool
def explain_cicd_error(error_log: str) -> str:
    """
    Analyses a CI/CD pipeline error log and explains what went wrong
    in plain English with specific fix suggestions.
    Use this when the user pastes a GitHub Actions, Jenkins,
    or any pipeline error or failure log.
    """
    return f"""
ANALYSIS REQUEST: CI/CD Error Log
-----------------------------------
{error_log}
-----------------------------------
Please analyse this CI/CD error log and provide:
1. ROOT CAUSE: What specifically caused this failure (be precise)
2. EXPLANATION: Why this happens in plain English
3. FIX: Exact steps to resolve it, including any commands to run
4. PREVENTION: How to prevent this error in future pipelines
"""


@tool
def explain_terraform_plan(plan_output: str) -> str:
    """
    Takes a terraform plan output and explains what infrastructure
    changes will happen in plain English, highlighting any risks.
    Use this when the user pastes output from 'terraform plan'.
    """
    return f"""
ANALYSIS REQUEST: Terraform Plan
-----------------------------------
{plan_output}
-----------------------------------
Please analyse this Terraform plan and provide:
1. SUMMARY: What will be created, modified, or destroyed (in plain English)
2. RISKS: Any potentially dangerous changes (deletions, replacements, security issues)
3. COST IMPACT: Likely cost implications if any
4. RECOMMENDATION: Whether it looks safe to apply and anything to double-check first
"""


@tool
def review_dockerfile(dockerfile_content: str) -> str:
    """
    Reviews a Dockerfile for security issues, best practice violations,
    and optimisation opportunities.
    Use this when the user pastes a Dockerfile for review.
    """
    return f"""
ANALYSIS REQUEST: Dockerfile Review
-----------------------------------
{dockerfile_content}
-----------------------------------
Please review this Dockerfile and provide:
1. SECURITY ISSUES: Any vulnerabilities or bad practices (running as root, etc.)
2. BEST PRACTICES: Violations of Docker best practices
3. OPTIMISATION: Ways to reduce image size or improve build speed
4. FIXED VERSION: Provide an improved version of the Dockerfile with comments
"""


@tool
def generate_runbook(incident_description: str) -> str:
    """
    Generates a structured incident runbook from a description
    of an infrastructure or application incident.
    Use this when the user describes an outage, incident, or
    asks for a runbook or incident response plan.
    """
    return f"""
RUNBOOK REQUEST: {incident_description}
-----------------------------------
Please generate a structured runbook with these sections:
1. INCIDENT SUMMARY: Brief description of the incident type
2. DETECTION: How to identify this incident is occurring (metrics, logs, alerts)
3. IMMEDIATE TRIAGE: First 5 minutes - what to check right away
4. INVESTIGATION STEPS: Numbered steps to diagnose root cause
5. RESOLUTION: Steps to resolve the incident
6. ROLLBACK PLAN: How to rollback if the fix makes things worse
7. POST-INCIDENT: What to do after resolution (postmortem, monitoring updates)
"""


@tool
def analyse_logs(log_snippet: str) -> str:
    """
    Analyses application or system log snippets to identify
    errors, patterns, anomalies, and recommended actions.
    Use this when the user pastes log output for analysis.
    """
    return f"""
ANALYSIS REQUEST: Log Analysis
-----------------------------------
{log_snippet}
-----------------------------------
Please analyse these logs and provide:
1. ERROR PATTERNS: Identified errors, exceptions, or warnings
2. TIMELINE: Sequence of events leading to any issues
3. ROOT CAUSE INDICATORS: What the logs suggest caused the problem
4. ANOMALIES: Anything unusual or unexpected in the log output
5. RECOMMENDED ACTIONS: Specific next steps based on what you see
"""