import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")

DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")

def get_connection():
    if IS_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def q(sql: str) -> str:
    """Format placeholders for SQLite (?) vs PostgreSQL (%s)."""
    if IS_POSTGRES:
        return sql.replace("?", "%s")
    return sql

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db(seed_if_empty: bool = True):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        pk_type = "SERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"

        # Users Table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                xp INTEGER DEFAULT 150,
                streak INTEGER DEFAULT 2,
                last_active_date TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Tasks Table (Parent Projects or Tasks)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS tasks (
                id {pk_type},
                user_id INTEGER DEFAULT 1,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT NOT NULL DEFAULT 'Development',
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'To Do',
                due_date TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Subtasks Table (Small tasks inside big tasks)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS subtasks (
                id {pk_type},
                task_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'To Do',
                due_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Schema migration check for user_id in tasks
        if not IS_POSTGRES:
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col["name"] for col in cursor.fetchall()]
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER DEFAULT 1")
            
            cursor.execute("PRAGMA table_info(subtasks)")
            sub_columns = [col["name"] for col in cursor.fetchall()]
            if "due_date" not in sub_columns:
                cursor.execute("ALTER TABLE subtasks ADD COLUMN due_date TEXT")

        # Ensure default demo user exists
        cursor.execute(q("SELECT COUNT(*) as c FROM users WHERE username = ?"), ("demo",))
        row = cursor.fetchone()
        c = row["c"] if isinstance(row, dict) else row[0]
        if c == 0:
            today_str = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(q("""
                INSERT INTO users (username, password_hash, xp, streak, last_active_date, created_at)
                VALUES (?, ?, 250, 3, ?, ?)
            """), ("demo", hash_password("demo123"), today_str, today_str))

        conn.commit()

        if seed_if_empty:
            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            r = cursor.fetchone()
            count = r["count"] if isinstance(r, dict) else r[0]
            if count == 0:
                seed_demo_data(conn)

def seed_demo_data(conn=None):
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks")
    cursor.execute("DELETE FROM tasks")
    
    today = datetime.now()
    t_today = today.strftime("%Y-%m-%d")
    t_in_5_days = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    t_in_15_days = (today + timedelta(days=15)).strftime("%Y-%m-%d")
    t_in_30_days = (today + timedelta(days=30)).strftime("%Y-%m-%d")

    demo_projects = [
        {
            "title": "Develop Full-Stack Web Application",
            "description": "Complete production-ready web platform with backend API, database, and responsive UI.",
            "category": "Development",
            "priority": "High",
            "status": "In Progress",
            "due_date": t_in_15_days,
            "subtasks": [
                ("Design Database Schema & Models", "Completed", t_today),
                ("Build RESTful CRUD API Endpoints", "Completed", t_today),
                ("Implement User Authentication & Sessions", "In Progress", t_in_5_days),
                ("Connect Frontend State to Backend API", "To Do", t_in_5_days),
                ("Conduct End-to-End Testing & Bug Fixes", "To Do", t_in_15_days)
            ]
        },
        {
            "title": "Prepare Final Semester Capstone (PFE)",
            "description": "Final graduation project deliverables, thesis documentation, and oral presentation.",
            "category": "Studies",
            "priority": "High",
            "status": "In Progress",
            "due_date": t_in_30_days,
            "subtasks": [
                ("Literature Review & System Requirements", "Completed", t_today),
                ("UML Architecture & Class Diagrams", "Completed", t_today),
                ("Prototype Implementation & Demos", "In Progress", t_in_15_days),
                ("Write Chapter 3: Implementation & Results", "To Do", t_in_30_days),
                ("Rehearse Final Defense Slide Deck", "To Do", t_in_30_days)
            ]
        },
        {
            "title": "Exam Revision & Practice Week",
            "description": "Comprehensive review of core computer science topics and past exam papers.",
            "category": "Studies",
            "priority": "Medium",
            "status": "To Do",
            "due_date": t_in_5_days,
            "subtasks": [
                ("Summarize Web Frameworks & MVC Architecture", "To Do", t_in_5_days),
                ("Solve Past Database & SQL Exam Papers", "To Do", t_in_5_days),
                ("Practice Algorithms & Complexity Analysis", "To Do", t_in_5_days)
            ]
        },
        {
            "title": "Healthy Lifestyle & Workout Habit",
            "description": "Daily athletic routine, nutrition planning, and hydration tracking.",
            "category": "Personal",
            "priority": "Low",
            "status": "To Do",
            "due_date": t_today,
            "subtasks": [
                ("Plan 4 Weekly Gym Workout Sessions", "Completed", t_today),
                ("Buy Wholesome Groceries & Protein Essentials", "To Do", t_today),
                ("Drink 2.5 Liters of Water Daily", "To Do", t_today)
            ]
        }
    ]

    for p in demo_projects:
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if IS_POSTGRES:
            cursor.execute(q("""
                INSERT INTO tasks (user_id, title, description, category, priority, status, due_date, created_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?) RETURNING id
            """), (p["title"], p["description"], p["category"], p["priority"], p["status"], p["due_date"], created))
            task_id = cursor.fetchone()["id"]
        else:
            cursor.execute(q("""
                INSERT INTO tasks (user_id, title, description, category, priority, status, due_date, created_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """), (p["title"], p["description"], p["category"], p["priority"], p["status"], p["due_date"], created))
            task_id = cursor.lastrowid

        for sub_item in p["subtasks"]:
            sub_title = sub_item[0]
            sub_status = sub_item[1]
            sub_due = sub_item[2] if len(sub_item) > 2 else None
            cursor.execute(q("""
                INSERT INTO subtasks (task_id, title, status, due_date, created_at)
                VALUES (?, ?, ?, ?, ?)
            """), (task_id, sub_title, sub_status, sub_due, created))

    conn.commit()
    if should_close:
        conn.close()

# ----------------- AUTH FUNCTIONS -----------------

def register_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT id FROM users WHERE username = ?"), (username.strip(),))
        if cursor.fetchone():
            return None

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if IS_POSTGRES:
            cursor.execute(q("""
                INSERT INTO users (username, password_hash, xp, streak, last_active_date, created_at)
                VALUES (?, ?, 150, 1, ?, ?) RETURNING id
            """), (username.strip(), hash_password(password), created_at[:10], created_at))
            user_id = cursor.fetchone()["id"]
        else:
            cursor.execute(q("""
                INSERT INTO users (username, password_hash, xp, streak, last_active_date, created_at)
                VALUES (?, ?, 150, 1, ?, ?)
            """), (username.strip(), hash_password(password), created_at[:10], created_at))
            user_id = cursor.lastrowid

        conn.commit()
        return {"id": user_id, "username": username.strip(), "xp": 150, "streak": 1}

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT * FROM users WHERE username = ?"), (username.strip(),))
        row = cursor.fetchone()
        if not row:
            return None
        
        row_dict = dict(row)
        if row_dict["password_hash"] == hash_password(password):
            return {
                "id": row_dict["id"],
                "username": row_dict["username"],
                "xp": row_dict["xp"],
                "streak": row_dict["streak"]
            }
        return None

def get_user_profile(user_id: int = 1) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT * FROM users WHERE id = ?"), (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT * FROM users LIMIT 1")
            row = cursor.fetchone()

        if not row:
            return {"id": 1, "username": "Guest", "xp": 150, "level": 2, "streak": 2, "level_name": "Consistent Organizer"}

        row_dict = dict(row)
        xp = row_dict["xp"]
        level = 1 + (xp // 100)
        level_names = [
            "Motivated Starter",
            "Consistent Organizer",
            "Efficient Planner",
            "Focus Master",
            "Productivity Legend"
        ]
        name_idx = min(len(level_names) - 1, level - 1)

        return {
            "id": row_dict["id"],
            "username": row_dict["username"],
            "xp": xp,
            "level": level,
            "level_name": level_names[name_idx],
            "streak": row_dict["streak"],
            "next_level_xp": level * 100
        }

def add_xp(amount: int, user_id: int = 1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("UPDATE users SET xp = xp + ? WHERE id = ?"), (amount, user_id))
        conn.commit()

# ----------------- SUBTASK FUNCTIONS -----------------

def get_subtasks_for_task(task_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC"), (task_id,))
        return [dict(row) for row in cursor.fetchall()]

def add_subtask(task_id: int, title: str, due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        if IS_POSTGRES:
            cursor.execute(q("""
                INSERT INTO subtasks (task_id, title, status, due_date, created_at)
                VALUES (?, ?, 'To Do', ?, ?) RETURNING id
            """), (task_id, title.strip(), due_date, created_at))
            sub_id = cursor.fetchone()["id"]
        else:
            cursor.execute(q("""
                INSERT INTO subtasks (task_id, title, status, due_date, created_at)
                VALUES (?, ?, 'To Do', ?, ?)
            """), (task_id, title.strip(), due_date, created_at))
            sub_id = cursor.lastrowid

        conn.commit()
        cursor.execute(q("SELECT * FROM subtasks WHERE id = ?"), (sub_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_subtask_status(subtask_id: int, status: str, user_id: int = 1) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT * FROM subtasks WHERE id = ?"), (subtask_id,))
        current = cursor.fetchone()
        if not current:
            return None

        current_dict = dict(current)
        cursor.execute(q("UPDATE subtasks SET status = ? WHERE id = ?"), (status, subtask_id))
        conn.commit()

        if status in ["Completed", "Terminée"] and current_dict["status"] not in ["Completed", "Terminée"]:
            add_xp(25, user_id)

        task_id = current_dict["task_id"]
        cursor.execute(q("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status IN ('Completed', 'Terminée') THEN 1 ELSE 0 END) as done 
            FROM subtasks WHERE task_id = ?
        """), (task_id,))
        stats = cursor.fetchone()
        stats_dict = dict(stats) if stats else {}
        total = stats_dict.get("total", 0)
        done = stats_dict.get("done", 0) or 0
        if total > 0 and total == done:
            cursor.execute(q("UPDATE tasks SET status = 'Completed' WHERE id = ?"), (task_id,))
            add_xp(50, user_id)
            conn.commit()

        cursor.execute(q("SELECT * FROM subtasks WHERE id = ?"), (subtask_id,))
        return dict(cursor.fetchone())

def delete_subtask(subtask_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("DELETE FROM subtasks WHERE id = ?"), (subtask_id,))
        conn.commit()
        return cursor.rowcount > 0

# ----------------- MAIN TASKS FUNCTIONS -----------------

def get_tasks(search: Optional[str] = None, status: Optional[str] = None, 
              priority: Optional[str] = None, category: Optional[str] = None,
              period: Optional[str] = None, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR id IN (SELECT task_id FROM subtasks WHERE title LIKE ?))"
        term = f"%{search}%"
        params.extend([term, term, term])
    if status and status not in ["All", "Toutes"]:
        query += " AND status = ?"
        params.append(status)
    if priority and priority not in ["All", "Toutes"]:
        query += " AND priority = ?"
        params.append(priority)
    if category and category not in ["All", "Toutes"]:
        query += " AND category = ?"
        params.append(category)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    if period == "today":
        query += " AND due_date = ?"
        params.append(today_str)
    elif period == "week":
        end_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        query += " AND due_date <= ?"
        params.append(end_week)
    elif period == "month":
        end_month = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        query += " AND due_date <= ?"
        params.append(end_month)
    elif period == "year":
        end_year = (today + timedelta(days=365)).strftime("%Y-%m-%d")
        query += " AND due_date <= ?"
        params.append(end_year)

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q(query), params)
        rows = cursor.fetchall()
        tasks = []
        for r in rows:
            t = dict(r)
            cursor.execute(q("SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC"), (t["id"],))
            sub_rows = [dict(s) for s in cursor.fetchall()]
            t["subtasks"] = sub_rows
            t["subtasks_total"] = len(sub_rows)
            t["subtasks_completed"] = sum(1 for s in sub_rows if s["status"] in ["Completed", "Terminée"])
            t["subtasks_progress"] = round((t["subtasks_completed"] / t["subtasks_total"] * 100), 1) if t["subtasks_total"] > 0 else (100.0 if t["status"] == "Completed" else 0.0)
            tasks.append(t)
        return tasks

def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("SELECT * FROM tasks WHERE id = ?"), (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        t = dict(row)
        cursor.execute(q("SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC"), (task_id,))
        sub_rows = [dict(s) for s in cursor.fetchall()]
        t["subtasks"] = sub_rows
        t["subtasks_total"] = len(sub_rows)
        t["subtasks_completed"] = sum(1 for s in sub_rows if s["status"] in ["Completed", "Terminée"])
        t["subtasks_progress"] = round((t["subtasks_completed"] / t["subtasks_total"] * 100), 1) if t["subtasks_total"] > 0 else 0.0
        return t

def create_task(data: dict, user_id: int = 1) -> Dict[str, Any]:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtasks = data.get("subtasks", [])
    with get_connection() as conn:
        cursor = conn.cursor()
        if IS_POSTGRES:
            cursor.execute(q("""
                INSERT INTO tasks (user_id, title, description, category, priority, status, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id
            """), (
                user_id,
                data["title"],
                data.get("description", ""),
                data.get("category", "Development"),
                data.get("priority", "Medium"),
                data.get("status", "To Do"),
                data.get("due_date"),
                created_at
            ))
            task_id = cursor.fetchone()["id"]
        else:
            cursor.execute(q("""
                INSERT INTO tasks (user_id, title, description, category, priority, status, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                user_id,
                data["title"],
                data.get("description", ""),
                data.get("category", "Development"),
                data.get("priority", "Medium"),
                data.get("status", "To Do"),
                data.get("due_date"),
                created_at
            ))
            task_id = cursor.lastrowid

        for sub in subtasks:
            sub_title = sub if isinstance(sub, str) else sub.get("title", "")
            sub_status = sub.get("status", "To Do") if isinstance(sub, dict) else "To Do"
            sub_due = sub.get("due_date") if isinstance(sub, dict) else None
            if sub_title.strip():
                cursor.execute(q("""
                    INSERT INTO subtasks (task_id, title, status, due_date, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """), (task_id, sub_title.strip(), sub_status, sub_due, created_at))
        conn.commit()

        return get_task(task_id)

def create_tasks_batch(tasks_list: List[dict], user_id: int = 1) -> List[Dict[str, Any]]:
    created_tasks = []
    for data in tasks_list:
        t = create_task(data, user_id)
        if t:
            created_tasks.append(t)
    return created_tasks

def update_task(task_id: int, data: dict, user_id: int = 1) -> Optional[Dict[str, Any]]:
    current = get_task(task_id)
    if not current:
        return None

    updated = {k: v for k, v in data.items() if v is not None and k != "subtasks"}
    if not updated:
        return current

    if updated.get("status") in ["Completed", "Terminée"] and current.get("status") not in ["Completed", "Terminée"]:
        add_xp(50, user_id)

    set_clause = ", ".join([f"{key} = ?" for key in updated.keys()])
    values = list(updated.values())
    values.append(task_id)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q(f"UPDATE tasks SET {set_clause} WHERE id = ?"), values)
        conn.commit()
        return get_task(task_id)

def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(q("DELETE FROM subtasks WHERE task_id = ?"), (task_id,))
        cursor.execute(q("DELETE FROM tasks WHERE id = ?"), (task_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_stats(user_id: int = 1) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM tasks")
        row = cursor.fetchone()
        total = dict(row)["total"] if row else 0

        cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE status IN ('To Do', 'À faire')")
        pending = dict(cursor.fetchone())["c"]

        cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE status IN ('In Progress', 'En cours')")
        in_progress = dict(cursor.fetchone())["c"]

        cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE status IN ('Completed', 'Terminée')")
        completed = dict(cursor.fetchone())["c"]

        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE status NOT IN ('Completed', 'Terminée') AND priority IN ('High', 'Haute')")
        urgent = dict(cursor.fetchone())["c"]

        cursor.execute(q("SELECT COUNT(*) as c FROM tasks WHERE status NOT IN ('Completed', 'Terminée') AND due_date < ?"), (today_str,))
        overdue = dict(cursor.fetchone())["c"]

        cursor.execute("SELECT COUNT(*) as total_sub, SUM(CASE WHEN status IN ('Completed', 'Terminée') THEN 1 ELSE 0 END) as done_sub FROM subtasks")
        sub_row = dict(cursor.fetchone())
        total_sub = sub_row["total_sub"] or 0
        done_sub = sub_row["done_sub"] or 0

        rate = round((completed / total * 100), 1) if total > 0 else 0.0
        profile = get_user_profile(user_id)

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "missing": pending + in_progress,
            "urgent": urgent,
            "overdue": overdue,
            "total_subtasks": total_sub,
            "completed_subtasks": done_sub,
            "completion_rate": rate,
            "profile": profile
        }

init_db(seed_if_empty=False)
