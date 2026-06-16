"""
agent.py — AI Agent for NayePankh AI Hub

The agent uses Grok's API (OpenAI-compatible) with tool calling.
It receives a user message, decides which tool to use, executes it,
and returns a grounded, human-readable response.

Tools:
  1. answer_faq          — RAG search over NayePankh knowledge base
  2. register_volunteer  — Save volunteer to SQLite DB with department match
  3. get_stats           — Read live volunteer statistics from DB
"""

# ─────────────────────────────────────────────
# SECTION 1 — IMPORTS
# ─────────────────────────────────────────────
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from rag import search_knowledge
from database import save_volunteer, get_stats, get_db


# ─────────────────────────────────────────────
# SECTION 2 — INITIALIZE GROK CLIENT
# ─────────────────────────────────────────────
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# ─────────────────────────────────────────────
# SECTION 3 — SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are Pakhi, the official AI assistant for NayePankh Foundation — \
a youth-led NGO uplifting underprivileged communities across India.

Your personality is warm, encouraging, and mission-driven.

You have access to three tools:
- answer_faq: use this for any question about NayePankh, its missions, \
how to donate, certificates, or general information
- register_volunteer: use this when a user wants to sign up or volunteer. \
Always collect name, email, skills, city, and hours per week before calling this.
- get_stats: use this when a user asks about volunteer numbers, \
impact stats, or dashboard data

Always stay on topic. If asked something unrelated to NayePankh, \
gently redirect the conversation back to the foundation's mission."""


# ─────────────────────────────────────────────
# SECTION 4 — TOOLS SCHEMA
# ─────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "answer_faq",
            "description": "Search NayePankh knowledge base to answer questions about the NGO",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question to search in the knowledge base"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_volunteer",
            "description": "Register a new volunteer in the database and match them to a department",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the volunteer"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address of the volunteer"
                    },
                    "skills": {
                        "type": "string",
                        "description": "Comma separated list of the volunteer's skills"
                    },
                    "city": {
                        "type": "string",
                        "description": "City where the volunteer is based"
                    },
                    "hours_per_week": {
                        "type": "integer",
                        "description": "Number of hours the volunteer can contribute per week"
                    }
                },
                "required": ["name", "email", "skills", "city", "hours_per_week"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Get current volunteer statistics and impact numbers from the database",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# ─────────────────────────────────────────────
# SECTION 5 — DEPARTMENT MATCHING
# ─────────────────────────────────────────────
DEPARTMENTS = {
    "Tech and Media":      ["python", "web", "coding", "design", "social media", "video", "java", "ml", "ai", "react"],
    "Education":           ["teaching", "tutoring", "content", "curriculum", "writing", "english"],
    "Food Relief":         ["logistics", "cooking", "distribution", "driving", "delivery"],
    "Women Empowerment":   ["awareness", "healthcare", "counseling", "social work", "ngo", "outreach"],
    "Fundraising":         ["marketing", "communication", "sales", "fundraising", "management"],
}


def match_department(skills: str) -> str:
    """
    Match a volunteer's skills string to the best-fit NayePankh department.
    Uses keyword frequency — the department with the most keyword hits wins.
    Falls back to 'General Volunteer' if no keywords match.
    """
    skills_lower = skills.lower()
    scores = {dept: 0 for dept in DEPARTMENTS}

    for dept, keywords in DEPARTMENTS.items():
        for keyword in keywords:
            if keyword in skills_lower:
                scores[dept] += 1

    best_dept = max(scores, key=scores.get)

    if scores[best_dept] == 0:
        return "General Volunteer"

    return best_dept


# ─────────────────────────────────────────────
# SECTION 6 — TOOL EXECUTION
# ─────────────────────────────────────────────
def execute_tool(tool_name: str, tool_args: dict) -> str:
    """
    Receives the tool name and arguments chosen by Grok,
    calls the actual Python function, and returns the result as a string.
    """

    # Tool 1 — RAG search
    if tool_name == "answer_faq":
        result = search_knowledge(tool_args["query"])
        return result

    # Tool 2 — Register volunteer
    if tool_name == "register_volunteer":
        try:
            department = match_department(tool_args["skills"])
            db = next(get_db())
            save_volunteer(
                db=db,
                name=tool_args["name"],
                email=tool_args["email"],
                skills=tool_args["skills"],
                city=tool_args["city"],
                hours_per_week=tool_args["hours_per_week"],
                department=department
            )
            return (
                f"Volunteer {tool_args['name']} registered successfully! "
                f"Matched to department: {department}"
            )
        except Exception:
            return "This email is already registered."

    # Tool 3 — Get stats
    if tool_name == "get_stats":
        db = next(get_db())
        stats = get_stats(db)
        lines = [
            f"Total Volunteers: {stats['total']}",
            "",
            "By Department:",
        ]
        for dept, count in stats["by_department"].items():
            lines.append(f"  - {dept}: {count}")
        lines.append("")
        lines.append("By City:")
        for city, count in stats["by_city"].items():
            lines.append(f"  - {city}: {count}")
        return "\n".join(lines)

    return "Unknown tool called."


# ─────────────────────────────────────────────
# SECTION 7 — MAIN CHAT FUNCTION
# ─────────────────────────────────────────────
def chat(messages: list) -> str:
    """
    Main entry point called by FastAPI.

    Args:
        messages: Full conversation history as list of
                  {"role": "user"/"assistant", "content": "..."} dicts.

    Returns:
        Final string response to show the user.
    """

    # Step 1 — Prepend system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Step 2 — First Grok API call (with tools)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=full_messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    # Step 3 — Check if Grok wants to call a tool
    if response_message.tool_calls:
        tool_call  = response_message.tool_calls[0]
        tool_name  = tool_call.function.name
        tool_args  = json.loads(tool_call.function.arguments)

        # Execute the tool
        tool_result = execute_tool(tool_name, tool_args)

        # Append assistant's tool-call message and tool result
        full_messages.append(response_message)
        full_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        # Step 4 — Second Grok API call to get final human-readable response
        final_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=full_messages
        )
        return final_response.choices[0].message.content

    # No tool call — return direct response
    return response_message.content
