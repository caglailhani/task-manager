# app.py — minimal login + Task UI (list/add/toggle/delete)
import os, requests, streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_BASE = os.getenv("AUTH_BASE", "/api/auth")  # backend login path base

st.set_page_config(page_title="Task Manager", page_icon="✅", layout="centered")

# --- clean styles ---
st.markdown("""
<style>
.block-container { padding-top: 3rem; max-width: 720px; }
h1 { margin-bottom: 1.2rem; letter-spacing:.3px; }
.login-card, .tasks-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px; padding: 22px 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.input-label { font-size:.86rem; opacity:.85; margin-bottom:6px; }
.btn-primary button {
  width:100%; border-radius:12px !important;
  padding:.7rem 1rem !important; font-weight:700 !important; letter-spacing:.5px !important;
}
.task-row { padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,.08); margin:6px 0; }
.task-row.done { opacity:.7; }
.task-title { font-weight:600; }
.task-desc { font-size:.9rem; opacity:.85; }
.badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:.78rem; margin-left:8px;
         border:1px solid rgba(255,255,255,.18); opacity:.9; }
</style>
""", unsafe_allow_html=True)

# ---------- Auth helpers ----------
def api_login(email: str, password: str):
    try:
        url = f"{BACKEND}{AUTH_BASE}/login"
        r = requests.post(url, json={"email": email, "password": password}, timeout=10)
        if r.status_code != 200:
            return None, f"Login failed ({r.status_code}): {r.text}"
        data = r.json()
        token = data.get("access_token") or data.get("token")
        role  = data.get("role")
        return {"token": token, "role": role, "email": email}, None
    except Exception as e:
        return None, f"Request error: {e}"

# ---------- Task API helpers ----------
def api_headers():
    a = st.session_state.get("auth") or {}
    t = a.get("token")
    return {"Authorization": f"Bearer {t}"} if t else {}

def tasks_list():
    try:
        r = requests.get(f"{BACKEND}/api/tasks", headers=api_headers(), timeout=10)
        if not r.ok:
            return []
        js = r.json()
        # API bazen { "items": [...] } döndürüyor
        if isinstance(js, dict) and isinstance(js.get("items"), list):
            return js["items"]
        # yoksa zaten listeyse onu döndür
        if isinstance(js, list):
            return js
        return []
    except Exception:
        return []

def task_create(title, description=""):
    try:
        r = requests.post(
            f"{BACKEND}/api/tasks",
            headers={**api_headers(), "Content-Type": "application/json"},
            json={"title": title, "description": description},
            timeout=10
        )
        return r.ok
    except Exception:
        return False

def task_toggle(task_id):
    try:
        r = requests.put(f"{BACKEND}/api/tasks/{task_id}/toggle", headers=api_headers(), timeout=10)
        return r.ok
    except Exception:
        return False

def task_delete(task_id):
    try:
        r = requests.delete(f"{BACKEND}/api/tasks/{task_id}", headers=api_headers(), timeout=10)
        return r.ok
    except Exception:
        return False
# -------------------------------------

def _is_done(t):
    """completed: bool veya status: 'done' ise True."""
    if isinstance(t, dict):
        if t.get("completed"):
            return True
        status = str(t.get("status", "")).lower()
        return status == "done" or status == "completed"
    return False

# session
if "auth" not in st.session_state:
    st.session_state.auth = None

# already logged in? -> Show Task UI
if st.session_state.auth and st.session_state.auth.get("token"):

    # ensure role/email via whoami (added)
    try:
        a = st.session_state.auth
        if not a.get("role") and a.get("token"):
            r = requests.get(
                f"{BACKEND}/whoami",
                headers={"Authorization": f"Bearer {a['token']}"},
                timeout=5
            )
            if r.ok:
                who = r.json()
                a["email"] = who.get("email", a.get("email"))
                a["role"]  = who.get("role")
    except Exception:
        pass

    # Header (logged-in info + logout)
    a = st.session_state.auth
    st.success(f"Signed in as **{a.get('email')}**  ·  role: **{a.get('role') or 'unknown'}**")
    if st.button("Logout"):
        st.session_state.auth = None
        st.rerun()

    # -------- Task UI --------
    st.subheader("Tasks", divider="gray")
    st.markdown('<div class="tasks-card">', unsafe_allow_html=True)

    # Add form
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 3])
        with c1:
            title = st.text_input("Title", key="new_title", placeholder="e.g., Fix login bug")
        with c2:
            desc = st.text_input("Description", key="new_desc", placeholder="optional")
        submitted = st.form_submit_button("Add Task", use_container_width=True)
        if submitted:
            if not title:
                st.error("Title is required.")
            elif task_create(title.strip(), desc.strip()):
                st.success("Task created.")
                st.rerun()
            else:
                st.error("Create failed.")

    # List + actions
    data = tasks_list()
    if not data:
        st.info("No tasks yet. Add your first task!")
    else:
        # show incomplete first, then completed
        data = sorted(data, key=lambda t: (_is_done(t), t.get("id", 0)))
        for t in data:
            done = _is_done(t)
            rid  = t.get("id")
            row_class = "task-row done" if done else "task-row"
            st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([6, 3, 2, 2])
            with c1:
                st.markdown(
                    f'<span class="task-title">{t.get("title","(no title)")}</span>'
                    f'<span class="badge">#{rid}</span>',
                    unsafe_allow_html=True
                )
                if t.get("description"):
                    st.markdown(f'<div class="task-desc">{t["description"]}</div>', unsafe_allow_html=True)
            with c2:
                st.write("✅ Completed" if done else "⏳ Pending")
            with c3:
                if st.button("Toggle", key=f"tgl-{rid}"):
                    if task_toggle(rid):
                        st.rerun()
                    else:
                        st.error("Toggle failed.")
            with c4:
                if st.button("Delete", key=f"del-{rid}"):
                    if task_delete(rid):
                        st.rerun()
                    else:
                        st.error("Delete failed.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
# -------- End of Task UI --------

# --- TITLE (login page) ---
st.title("Task Manager")

# --- LOGIN CARD ---
st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.subheader("User Login", divider="gray")
with st.form("login_form", clear_on_submit=False):
    st.markdown('<div class="input-label">Email</div>', unsafe_allow_html=True)
    email = st.text_input("Email", key="login_email", placeholder="you@example.com", label_visibility="collapsed")

    st.markdown('<div class="input-label" style="margin-top:10px;">Password</div>', unsafe_allow_html=True)
    password = st.text_input("Password", key="login_password", type="password", placeholder="••••••••", label_visibility="collapsed")

    submitted = st.form_submit_button("LOGIN", use_container_width=True)
    if submitted:
        if not email or not password:
            st.error("Please enter email and password.")
        else:
            auth, err = api_login(email.strip(), password)
            if err:
                st.error(err)
            elif not auth or not auth.get("token"):
                st.error("Missing token in response.")
            else:
                st.session_state.auth = auth
                st.success("Logged in!")
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
