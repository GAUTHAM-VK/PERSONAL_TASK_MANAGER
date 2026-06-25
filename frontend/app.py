import requests
import streamlit as st
from pathlib import Path
from datetime import date
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
st.set_page_config(
    page_title="Personal Task Manager",
    page_icon="✅",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
def load_custom_css():
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #050816 0%, #0b1220 45%, #111827 100%);
        color: #f8fafc;
    }

    /* Main content width/padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #131a2b 0%, #1f2937 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* Brand / hero */
    .brand-pill {
        display: inline-block;
        background: linear-gradient(90deg, #22c55e, #06b6d4);
        color: white;
        padding: 0.4rem 0.95rem;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 10px 24px rgba(6, 182, 212, 0.28);
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        color: #ffffff;
        margin-bottom: 0.6rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        line-height: 1.7;
        margin-bottom: 1.2rem;
    }

    .hero-small {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.4rem;
    }

    /* Glass card */
    .glass-card {
        background: rgba(17, 24, 39, 0.78);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.6rem;
        box-shadow: 0 18px 40px rgba(0,0,0,0.35);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 1.2rem;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .section-caption {
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input {
        background-color: rgba(255,255,255,0.06) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
    }

    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.06) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.72rem 1rem !important;
        background: linear-gradient(90deg, #2563eb, #06b6d4) !important;
        color: white !important;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.35);
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        filter: brightness(1.06);
        transform: translateY(-1px);
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background: rgba(17, 24, 39, 0.72);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }

    /* Task cards */
    .task-card {
        background: rgba(17, 24, 39, 0.72);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }

    .task-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }

    .task-meta {
        color: #cbd5e1;
        font-size: 0.95rem;
    }

    .status-badge, .priority-badge {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.5rem;
        margin-bottom: 0.35rem;
    }

    .priority-low { background: rgba(34,197,94,0.18); color: #86efac; }
    .priority-medium { background: rgba(245,158,11,0.18); color: #fcd34d; }
    .priority-high { background: rgba(239,68,68,0.18); color: #fca5a5; }

    .status-pending { background: rgba(59,130,246,0.18); color: #93c5fd; }
    .status-inprogress { background: rgba(168,85,247,0.18); color: #d8b4fe; }
    .status-done { background: rgba(34,197,94,0.18); color: #86efac; }

    hr {
        border-color: rgba(255,255,255,0.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# =========================
# API HELPER
# =========================
def api_call(method: str, endpoint: str, data: dict | None = None, token: str | None = None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the server. Is the FastAPI backend running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

    if response.status_code == 204:
        return True, None

    try:
        body = response.json()
    except ValueError:
        body = response.text

    if response.ok:
        return True, body

    detail = body.get("detail") if isinstance(body, dict) else body
    return False, str(detail)

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "token" not in st.session_state:
    st.session_state["token"] = None
if "email" not in st.session_state:
    st.session_state["email"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "selected_task_id" not in st.session_state:
    st.session_state["selected_task_id"] = None
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

def goto(page: str):
    st.session_state["page"] = page
    st.rerun()

# =========================
# IMAGE
# =========================
def show_banner_image():
    image_path = Path("assets/task_manager_banner.jpg")
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.info("Add your image here: assets/task_manager_banner.jpg")

# =========================
# UI HELPERS
# =========================
def render_auth_hero(subtitle: str):
    st.markdown('<div class="brand-pill">ABC</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Personal Task Manager</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    show_banner_image()
    st.markdown(
        '<div class="hero-small">Manage tasks, priorities, deadlines, and progress from one workspace.</div>',
        unsafe_allow_html=True
    )

def render_dashboard_header(title: str, subtitle: str):
    st.markdown(f'<div class="hero-title" style="font-size:2.45rem;">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def get_priority_badge(priority: str):
    cls = f"priority-{priority}"
    return f'<span class="priority-badge {cls}">{priority.upper()}</span>'

def get_status_badge(status: str):
    cls_map = {
        "pending": "status-pending",
        "in-progress": "status-inprogress",
        "done": "status-done"
    }
    cls = cls_map.get(status, "status-pending")
    return f'<span class="status-badge {cls}">{status.upper()}</span>'

# =========================
# SIDEBAR
# =========================
def render_sidebar():
    with st.sidebar:
        st.markdown("## ABC")
        st.caption("Personal Task Manager")

        # show username instead of email
        if st.session_state["username"]:
            st.write(f"Logged in as **{st.session_state['username']}**")
        elif st.session_state["email"]:
            st.write(f"Logged in as **{st.session_state['email']}**")

        if st.button("Dashboard", use_container_width=True):
            goto("dashboard")

        st.divider()

        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# =========================
# REGISTER PAGE
# =========================
def page_register():
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        render_auth_hero(
            "Create your personal workspace to organize tasks, set priorities, and stay productive every day."
        )

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Create an account</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Register to start using Personal Task Manager.</div>',
            unsafe_allow_html=True
        )

        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not username.strip() or not email.strip() or not password.strip():
                st.error("Username, email and password cannot be empty.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                payload = {
                    "username": username,
                    "email": email,
                    "password": password
                }
                ok, result = api_call("POST", "/auth/register", payload)
                if ok:
                    st.success("Account created! Please log in.")
                    goto("login")
                else:
                    st.error(result)

        st.caption("Already have an account?")
        if st.button("Go to Login"):
            goto("login")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================
def page_login():
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        render_auth_hero(
            "Plan your day, organize priorities, track deadlines, and manage tasks efficiently in one modern workspace."
        )

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Log in</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Welcome back. Sign in to continue managing your tasks.</div>',
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email.strip() or not password.strip():
                st.error("Email and password cannot be empty.")
            else:
                with st.spinner("Logging in..."):
                    ok, result = api_call("POST", "/auth/login", {"email": email, "password": password})
                if ok:
                    st.session_state["token"] = result["access_token"]
                    st.session_state["email"] = result.get("email")
                    st.session_state["username"] = result.get("username")
                    goto("dashboard")
                else:
                    st.error(result)

        st.caption("Don't have an account?")
        if st.button("Go to Register"):
            goto("register")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DASHBOARD PAGE
# =========================
def page_dashboard():
    render_sidebar()
    render_dashboard_header(
        "Dashboard",
        "Track your tasks, completion progress, priorities, search tasks, and add new tasks in one place."
    )

    token = st.session_state["token"]

    # Summary
    with st.spinner("Loading summary..."):
        ok, summary = api_call("GET", "/tasks/summary", token=token)

    if not ok:
        st.error(summary)
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", summary["total"])
    c2.metric("Pending", summary["pending"])
    c3.metric("Done", summary["done"])

    st.divider()

    # Add task inside dashboard
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Add New Task</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Create a new task directly from your dashboard.</div>',
        unsafe_allow_html=True
    )

    with st.form("dashboard_add_task_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Task Title")
            description = st.text_area("Description")

        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
            due_date = st.date_input("Due date", value=date.today())

        submitted = st.form_submit_button("Create Task", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Title cannot be empty.")
        else:
            payload = {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": str(due_date) if due_date else None,
            }

            with st.spinner("Creating task..."):
                ok_create, result = api_call("POST", "/tasks", payload, token=token)

            if ok_create:
                st.success("Task created successfully!")
                st.rerun()
            else:
                st.error(result)

    st.markdown('</div>', unsafe_allow_html=True)

    # Search + filter
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Task List</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Search tasks and filter them by status and priority.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("Search Task", placeholder="Search by title or description")

    with col2:
        status_filter = st.selectbox("Filter by status", ["All", "pending", "in-progress", "done"])

    with col3:
        priority_filter = st.selectbox("Filter by priority", ["All", "low", "medium", "high"])

    params = []
    if status_filter != "All":
        params.append(f"status_filter={status_filter}")
    if priority_filter != "All":
        params.append(f"priority={priority_filter}")

    query_string = ("?" + "&".join(params)) if params else ""

    with st.spinner("Loading tasks..."):
        ok, tasks = api_call("GET", f"/tasks{query_string}", token=token)

    if not ok:
        st.error(tasks)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Frontend search
    if search_query.strip():
        q = search_query.strip().lower()
        tasks = [
            task for task in tasks
            if q in task["title"].lower()
            or q in (task.get("description") or "").lower()
        ]

    if not tasks:
        st.info("No tasks found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for task in tasks:
        st.markdown('<div class="task-card">', unsafe_allow_html=True)

        row1, row2 = st.columns([5, 2])

        with row1:
            st.markdown(f'<div class="task-title">{task["title"]}</div>', unsafe_allow_html=True)
            desc = task.get("description") or "No description"
            st.markdown(f'<div class="task-meta">{desc}</div>', unsafe_allow_html=True)

        with row2:
            st.markdown(
                get_priority_badge(task["priority"]) + get_status_badge(task["status"]),
                unsafe_allow_html=True
            )

        col_a, col_b, col_c, col_d = st.columns([3, 2, 1.2, 1.8])

        due_text = task["due_date"] if task["due_date"] else "No due date"
        col_a.caption(f"Due date: {due_text}")
        col_b.caption(f"Task ID: {task['id']}")

        if col_c.button("View", key=f"view_{task['id']}"):
            st.session_state["selected_task_id"] = task["id"]
            goto("task_detail")

        if task["status"] != "done":
            if col_d.button("Mark as Done", key=f"done_{task['id']}"):
                with st.spinner("Updating..."):
                    ok2, result = api_call(
                        "PATCH",
                        f"/tasks/{task['id']}/status",
                        {"status": "done"},
                        token=token
                    )
                if ok2:
                    st.rerun()
                else:
                    st.error(result)
        else:
            col_d.caption("Completed")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TASK DETAIL PAGE
# =========================
def page_task_detail():
    render_sidebar()
    render_dashboard_header("Task Detail", "View full task information and manage task actions.")

    task_id = st.session_state["selected_task_id"]
    token = st.session_state["token"]

    with st.spinner("Loading task..."):
        ok, task = api_call("GET", f"/tasks/{task_id}", token=token)

    if not ok:
        st.error(task)
        if st.button("Back to Dashboard"):
            goto("dashboard")
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.subheader(task["title"])
    st.write(task["description"] or "_No description_")
    st.markdown(
        get_priority_badge(task["priority"]) + get_status_badge(task["status"]),
        unsafe_allow_html=True
    )
    st.caption(f"Due: {task['due_date'] or 'N/A'}")

    col1, col2, col3 = st.columns(3)

    if col1.button("Edit", use_container_width=True):
        goto("edit_task")

    if col2.button("Delete", use_container_width=True):
        st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete"):
        st.warning("Are you sure you want to delete this task? This cannot be undone.")
        c1, c2 = st.columns(2)
        if c1.button("Yes, delete it"):
            ok2, result = api_call("DELETE", f"/tasks/{task_id}", token=token)
            if ok2:
                st.session_state["confirm_delete"] = False
                st.success("Task deleted.")
                goto("dashboard")
            else:
                st.error(result)
        if c2.button("Cancel"):
            st.session_state["confirm_delete"] = False
            st.rerun()

    if col3.button("Back", use_container_width=True):
        goto("dashboard")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# EDIT TASK PAGE
# =========================
def page_edit_task():
    render_sidebar()
    render_dashboard_header("Edit Task", "Update the selected task details.")

    task_id = st.session_state["selected_task_id"]
    token = st.session_state["token"]

    with st.spinner("Loading task..."):
        ok, task = api_call("GET", f"/tasks/{task_id}", token=token)

    if not ok:
        st.error(task)
        if st.button("Back to Dashboard"):
            goto("dashboard")
        return

    priority_options = ["low", "medium", "high"]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    with st.form("edit_task_form"):
        title = st.text_input("Title", value=task["title"])
        description = st.text_area("Description", value=task["description"] or "")
        priority = st.selectbox(
            "Priority", priority_options, index=priority_options.index(task["priority"])
        )
        due_date = st.text_input("Due date (YYYY-MM-DD)", value=task["due_date"] or "")
        submitted = st.form_submit_button("Save Changes", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Title cannot be empty.")
        else:
            payload = {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date or None,
            }
            with st.spinner("Saving..."):
                ok2, result = api_call("PUT", f"/tasks/{task_id}", payload, token=token)
            if ok2:
                st.success("Task updated!")
                goto("task_detail")
            else:
                st.error(result)

    if st.button("Cancel"):
        goto("task_detail")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ROUTER
# =========================
page = st.session_state["page"]

if page == "register":
    page_register()
elif page == "login":
    page_login()
elif page == "dashboard":
    page_dashboard()
elif page == "task_detail":
    page_task_detail()
elif page == "edit_task":
    page_edit_task()
else:
    page_login()