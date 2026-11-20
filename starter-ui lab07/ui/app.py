"""Streamlit chat UI.   Run:  streamlit run ui/app.py      (the API must be running on port 8000)

The UI never imports assistant_core: it only talks to the backend through the HTTP API.
"""
import os
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # so "import ui..." works under streamlit

from ui.api_client import AssistantClient
from ui.logic import EXAMPLES, WELCOME, set_rating, status_note, validate_input, word_stream

st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
client = AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000"))

# ---- session state: remembered between reruns of this script ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rated" not in st.session_state:
    st.session_state.rated = {}   # request_id -> last rating (1 or -1)

st.title("🎓 FIT Study Assistant")
if not client.healthy():
    st.error("The assistant backend is not reachable. Start it with: uvicorn assistant_api.main:create_app --factory")

with st.sidebar:
    st.subheader("Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex
    st.caption("This is an AI assistant. Check important decisions with the Training Office.")

# ---- history -------------------------------------------------------------------
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander(f"📄 Sources ({len(m['sources'])})"):
                for s in m["sources"]:
                    st.markdown(f"**{s['title']}**")
                    st.caption(s["id"])
        if m.get("note"):
            st.info(m["note"])
        rid = m.get("request_id")
        if rid:
            current = st.session_state.rated.get(rid)
            c1, c2, c3 = st.columns([1, 1, 6])
            if c1.button("👍", key=f"up{i}", type="primary" if current == 1 else "secondary"):
                if set_rating(st.session_state.rated, rid, 1):
                    client.send_feedback(rid, 1)
                    st.toast("Thanks for your feedback!")
                    st.rerun()
            if c2.button("👎", key=f"down{i}", type="primary" if current == -1 else "secondary"):
                if set_rating(st.session_state.rated, rid, -1):
                    client.send_feedback(rid, -1)
                    st.toast("Thanks — we will look at this answer.")
                    st.rerun()
            if current:
                c3.caption("You rated this " + ("👍" if current == 1 else "👎") + " — click the other to change.")
# ---- new question ----------------------------------------------------------------
question = st.chat_input("Ask about fees, offices or the handbook…") or st.session_state.pop("pending", None)
if question:
    problem = validate_input(question)
    if problem:
        st.warning(problem)
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.spinner("Thinking…"):
            result = client.ask(question, st.session_state.session_id)
        if result.ok:
            with st.chat_message("assistant"):
                st.write_stream(word_stream(result.answer))   # typing effect, shown once
            st.session_state.messages.append({"role": "assistant", "content": result.answer,
                                              "sources": result.sources,
                                              "note": status_note(result), "request_id": result.request_id})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
        st.rerun()
