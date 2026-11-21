"""
AI Assistant Module for TaskFlow
Powered by Groq's high-speed 120B LLM (openai/gpt-oss-120b) with local fallback.
Intelligently breaks down any project, goal, or assignment into realistic, scheduled actionable tasks.
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def call_groq_llm(project_title: str, total_days: int, target_steps: int) -> Optional[List[Dict[str, Any]]]:
    """Call Groq API using 120B LLM for intelligent, context-aware project breakdown."""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return None

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)

        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = (
            f"You are an expert project planner and software architect. "
            f"Decompose the following user project into exactly {target_steps} actionable, high-quality milestones:\n"
            f"Project: \"{project_title}\"\n"
            f"Total timeline: {total_days} days starting from today ({today_str}).\n\n"
            f"Return ONLY a valid JSON array of {target_steps} objects. "
            f"Each object must have these exact keys:\n"
            f"- \"title\": concise, professional milestone title (e.g. \"Setup Database Schema & Models\")\n"
            f"- \"description\": detailed, actionable description of what to do\n"
            f"- \"category\": choose one from [\"Development\", \"Studies\", \"Personal\", \"Work\"]\n"
            f"- \"priority\": choose one from [\"High\", \"Medium\", \"Low\"]\n"
            f"- \"due_date\": YYYY-MM-DD distributed logically across the {total_days} days.\n"
            f"Do not include any text before or after the JSON array."
        )

        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=1500
        )

        raw = resp.choices[0].message.content.strip()
        # Clean any markdown code blocks
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)
        if isinstance(parsed, list) and len(parsed) > 0:
            valid_tasks = []
            for item in parsed:
                cat = item.get("category", "Development")
                if cat not in ["Development", "Studies", "Personal", "Work"]:
                    cat = "Development"
                prio = item.get("priority", "Medium")
                if prio not in ["High", "Medium", "Low"]:
                    prio = "Medium"

                valid_tasks.append({
                    "title": item.get("title", f"Milestone for {project_title}"),
                    "description": item.get("description", f"Action item for {project_title}"),
                    "category": cat,
                    "priority": prio,
                    "status": "To Do",
                    "due_date": item.get("due_date", today_str)
                })
            return valid_tasks
    except Exception as e:
        print(f"[AI Assistant] Groq LLM failed: {e}. Falling back to heuristic engine.")
        return None

def generate_project_tasks(
    project_title: str, 
    horizon: str = "auto", 
    custom_days: Optional[int] = None,
    num_steps: Optional[int] = None
) -> List[Dict[str, Any]]:
    today = datetime.now()
    title_lower = project_title.lower()

    # Determine Domain defaults
    if any(k in title_lower for k in ["pfe", "capstone", "thesis", "final project", "presentation", "report", "soutenance"]):
        auto_days = 90
        auto_steps = 5
    elif any(k in title_lower for k in ["web", "app", "mobile", "site", "code", "dev", "backend", "frontend", "api", "software", "game"]):
        auto_days = 30
        auto_steps = 5
    elif any(k in title_lower for k in ["exam", "test", "study", "revision", "course", "assignment", "homework", "school", "ds", "tp"]):
        auto_days = 14
        auto_steps = 4
    elif any(k in title_lower for k in ["workout", "fitness", "gym", "health", "diet", "running", "sport"]):
        auto_days = 45
        auto_steps = 5
    elif any(k in title_lower for k in ["travel", "trip", "vacation", "holiday", "flight"]):
        auto_days = 21
        auto_steps = 4
    else:
        auto_days = 30
        auto_steps = 5

    # Determine Total Days
    if custom_days and custom_days > 0:
        total_days = custom_days
    elif horizon == "week":
        total_days = 7
    elif horizon == "2weeks":
        total_days = 14
    elif horizon == "month":
        total_days = 30
    elif horizon == "3months":
        total_days = 90
    elif horizon == "year":
        total_days = 365
    else:
        total_days = auto_days

    # Determine Number of Steps
    target_steps = num_steps if (num_steps and 1 <= num_steps <= 15) else auto_steps

    # 1. First attempt: Real 120B LLM via Groq
    llm_tasks = call_groq_llm(project_title, total_days, target_steps)
    if llm_tasks:
        return llm_tasks

    # 2. Fallback heuristic engine if offline
    return generate_fallback_tasks(project_title, total_days, target_steps)

def generate_fallback_tasks(project_title: str, total_days: int, target_steps: int) -> List[Dict[str, Any]]:
    today = datetime.now()
    title_lower = project_title.lower()

    if any(k in title_lower for k in ["pfe", "capstone", "thesis", "report"]):
        base = [
            ("Define Scope, Problem Statement & Deliverables", "Draft primary objectives, constraints, and project charter.", "Studies", "High"),
            ("Literature Review & Benchmark Existing Systems", "Analyze existing solutions, research papers, and technical stack.", "Studies", "Medium"),
            ("System Architecture & Database Entity Modeling", "Design UML/ER diagrams, component architecture, and schemas.", "Development", "High"),
            ("Develop Core Backend & Data Persistence Layer", "Implement core APIs, business rules, and database CRUD operations.", "Development", "High"),
            ("Implement Interactive Frontend User Interface", "Develop responsive screens, navigation flow, and state handling.", "Development", "High"),
            ("Integration, Automated Testing & Verification", "Perform unit tests, API integration, and fix identified issues.", "Development", "Medium"),
            ("Draft Thesis Document & Final Presentation Prep", "Polish slides, rehearse oral demo, and finalize documentation.", "Studies", "High")
        ]
    elif any(k in title_lower for k in ["web", "app", "mobile", "site", "code", "dev", "backend", "frontend", "game"]):
        base = [
            ("Project Scope, User Stories & Wireframes", "Define target features, sketch screen layouts, and specify flows.", "Development", "Medium"),
            ("Setup Project Structure & Install Dependencies", "Initialize application workspace and configure build tools.", "Development", "Medium"),
            ("Design Database Schema & Models", "Create tables, relationship constraints, and initial mock fixtures.", "Development", "High"),
            ("Implement Core Backend API & Services", "Code primary endpoints, request validation, and database operations.", "Development", "High"),
            ("Build Responsive Frontend Pages", "Develop UI layout, responsive grids, buttons, and form components.", "Development", "High"),
            ("Connect Frontend to Backend REST API", "Wire API client, state management, and real-time response handlers.", "Development", "High"),
            ("Run Testing, Bug Fixing & Cross-Device Review", "Test across screen sizes and resolve edge-case glitches.", "Development", "Medium")
        ]
    elif any(k in title_lower for k in ["exam", "test", "study", "revision", "course"]):
        base = [
            ("Gather All Course Materials & Past Exam Papers", "Collect lecture slides, assignment sheets, and reference notes.", "Studies", "Medium"),
            ("Create Summary Cheatsheets for Key Chapters", "Condense complex concepts, definitions, and essential theorems.", "Studies", "High"),
            ("Solve Foundational Practice Exercises", "Work through standard application problems step-by-step.", "Studies", "High"),
            ("Tackle Difficult Edge-Case Problem Sets", "Identify weak spots and clarify questions with peers or teachers.", "Studies", "High"),
            ("Timed Mock Exam Simulation", "Complete a full exam paper under strict timed conditions.", "Studies", "High"),
            ("Final High-Yield Formula Review & Mental Rest", "Light conceptual recap and adequate rest before the exam.", "Personal", "Low")
        ]
    else:
        base = [
            (f"Define Clear Goals & Success Criteria for {project_title}", "Specify measurable milestones and required resources.", "Work", "High"),
            (f"Research Prerequisites & Select Tools", "Gather background data, best practices, and set up workspace.", "Work", "Medium"),
            (f"Execute Phase 1: High-Impact Core Actions", "Tackle the most important high-leverage milestones with focus.", "Work", "High"),
            (f"Execute Phase 2: Secondary Features & Details", "Develop supporting elements and expand project scope smoothly.", "Work", "High"),
            (f"Testing, Refinement & Final Quality Review", "Verify complete checklist and celebrate project completion.", "Work", "Medium")
        ]

    # Select target_steps items
    selected = []
    for i in range(target_steps):
        idx = int(round(i * (len(base) - 1) / (target_steps - 1))) if target_steps > 1 else 0
        idx = min(idx, len(base) - 1)
        selected.append(base[idx])

    result = []
    for idx, (title, desc, cat, prio) in enumerate(selected):
        ratio = (idx + 1) / target_steps
        offset = max(1, int(round(total_days * ratio)))
        due_date = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
        result.append({
            "title": f"{title}",
            "description": f"{desc} ({project_title})",
            "category": cat,
            "priority": prio,
            "status": "To Do",
            "due_date": due_date
        })
    return result
