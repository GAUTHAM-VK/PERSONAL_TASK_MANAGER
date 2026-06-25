import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Return a new PostgreSQL connection.
    """
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "task_manager_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "vkcode"),
    )
    return conn


def init_db():
    """Create the users and tasks tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
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
    cursor.close()
    conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_user(username: str, email: str, hashed_password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s) RETURNING id",
        (username, email, hashed_password),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def create_task(title, description, priority, status, due_date, owner_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tasks (title, description, priority, status, due_date, owner_email)
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
        (title, description, priority, status, due_date, owner_email),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return get_task_by_id(new_id)


def get_tasks_for_user(owner_email: str, status: str | None = None, priority: str | None = None):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM tasks WHERE owner_email = %s"
    params = [owner_email]

    if status:
        query += " AND status = %s"
        params.append(status)
    if priority:
        query += " AND priority = %s"
        params.append(priority)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_task_by_id(task_id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_task(task_id: int, title, description, priority, due_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE tasks
           SET title = %s, description = %s, priority = %s, due_date = %s
           WHERE id = %s""",
        (title, description, priority, due_date, task_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return get_task_by_id(task_id)


def update_task_status(task_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
    conn.commit()
    cursor.close()
    conn.close()
    return get_task_by_id(task_id)


def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_task_summary(owner_email: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT status, COUNT(*) as count FROM tasks WHERE owner_email = %s GROUP BY status",
        (owner_email,),
    )
    rows = cursor.fetchall()

    cursor.close()
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