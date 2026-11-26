"""Streamlit chat UI communicating exclusively over HTTP with the backend API."""

import os
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow ui imports under streamlit

from ui.api_client import AssistantClient
from ui.logic import EXAMPLES, WELCOME, format_sources, set_rating, status_note, validate_input, word_stream

st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
client = AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000"))

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rated" not in st.session_state:
    st.session_state.rated = {}  # map request_id to latest rating

st.title("🎓 FIT Study Assistant")
if not client.healthy():
    st.error("The assistant backend is not reachable. Start it with: uvicorn assistant_api.main:create_app --factory")

with st.sidebar:
    st.subheader("Try an example")
    for example in EXAMPLES:
        if st.button(example, use_container_width=True):
            st.session_state.pending = example
    st.caption("This is an AI assistant. Check important decisions with the Training Office.")

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(format_sources(msg["sources"]))  # show formatted source line
            with st.expander(f"📄 Sources ({len(msg['sources'])})"):
                for src in msg["sources"]:
                    st.markdown(f"**{src['title']}**")
                    st.caption(src["id"])
        if msg.get("note"):
            st.info(msg["note"])
        rid = msg.get("request_id")
        if rid:
            current = st.session_state.rated.get(rid)
            col_up, col_down, col_info = st.columns([1, 1, 6])
            if col_up.button("👍", key=f"up{idx}", type="primary" if current == 1 else "secondary"):
                if set_rating(st.session_state.rated, rid, 1):
                    client.send_feedback(rid, 1)
                    st.toast("Thanks for your feedback!")
                    st.rerun()
            if col_down.button("👎", key=f"down{idx}", type="primary" if current == -1 else "secondary"):
                if set_rating(st.session_state.rated, rid, -1):
                    client.send_feedback(rid, -1)
                    st.toast("Thanks — we will look at this answer.")
                    st.rerun()
            if current:
                col_info.caption("You rated this " + ("👍" if current == 1 else "👎") + " — click the other to change.")

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
                st.write_stream(word_stream(result.answer))  # stream words once for typing effect
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.answer,
                    "sources": result.sources,
                    "note": status_note(result),
                    "request_id": result.request_id,
                }
            )
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
        st.rerun()
