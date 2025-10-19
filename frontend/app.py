# app.py — minimal login only (title + email/password + login) with /api/auth base
import os, requests, streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_BASE = os.getenv("AUTH_BASE", "/api/auth")  # backend login path base

st.set_page_config(page_title="Task Manager", page_icon="✅", layout="centered")

# --- clean styles ---
st.markdown("""
<style>
.block-container { padding-top: 3rem; max-width: 520px; }
h1 { margin-bottom: 1.2rem; letter-spacing:.3px; }
.login-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px; padding: 28px 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.input-label { font-size:.86rem; opacity:.85; margin-bottom:6px; }
.btn-primary button {
  width:100%; border-radius:12px !important;
  padding:.7rem 1rem !important; font-weight:700 !important; letter-spacing:.5px !important;
}
</style>
""", unsafe_allow_html=True)

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

# session
if "auth" not in st.session_state:
    st.session_state.auth = None

# already logged in? (sade mesaj + logout)
# already logged in? (sade mesaj + logout)
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

    a = st.session_state.auth
    st.success(f"Signed in as **{a.get('email')}**  ·  role: **{a.get('role') or 'unknown'}**")
    if st.button("Logout"):
        st.session_state.auth = None
        st.rerun()
    st.stop()


# --- TITLE ---
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
