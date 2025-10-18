import os, requests, streamlit as st
BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("Task Manager Frontend")
st.caption(f"Backend: {BACKEND}")
if st.button("Check Backend Health"):
    try:
        r = requests.get(f"{BACKEND}/health", timeout=5)
        st.success(r.json())
    except Exception as e:
        st.error(f"Health check failed: {e}")
