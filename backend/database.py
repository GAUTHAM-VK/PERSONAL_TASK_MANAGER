import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent / "app.db"
def get_connection():
    """Return a new connection. Row factory lets us access columns by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    """Create the users and tasks tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
            status TEXT NOT NULL CHECK (status IN ('pending', 'in-progress', 'done')),
            due_date TEXT,
            owner_email TEXT NOT NULL,
            FOREIGN KEY (owner_email) REFERENCES users (email)
        )
    """)
    conn.commit()
    conn.close()

def get_user_by_email(email: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return row
def create_user(email: str, hashed_password: str):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
        (email, hashed_password),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def create_task(title, description, priority, status, due_date, owner_email):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO tasks (title, description, priority, status, due_date, owner_email)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, priority, status, due_date, owner_email),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_task_by_id(new_id)


def get_tasks_for_user(owner_email: str, status: str | None = None, priority: str | None = None):
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE owner_email = ?"
    params = [owner_email]

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_task_by_id(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row


def update_task(task_id: int, title, description, priority, due_date):
    conn = get_connection()
    conn.execute(
        """UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ?
           WHERE id = ?""",
        (title, description, priority, due_date, task_id),
    )
    conn.commit()
    conn.close()
    return get_task_by_id(task_id)


def update_task_status(task_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    return get_task_by_id(task_id)


def delete_task(task_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_task_summary(owner_email: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT status, COUNT(*) as count FROM tasks WHERE owner_email = ? GROUP BY status",
        (owner_email,),
    ).fetchall()
    conn.close()

    summary = {"total": 0, "pending": 0, "in_progress": 0, "done": 0}
    for row in rows:
        count = row["count"]
        summary["total"] += count
        if row["status"] == "pending":
            summary["pending"] = count
        elif row["status"] == "in-progress":
            summary["in_progress"] = count
        elif row["status"] == "done":
            summary["done"] = count
    return summary
