"""Kamilisha prototype screen. Run from the 06-prototype folder:  streamlit run app/app.py"""
import os, sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kamilisha as k

st.set_page_config(page_title="Kamilisha", page_icon="📘", layout="wide")
k.load_dotenv()

EXAMPLES = {
    "Card replacement": "Customer lost their card, what do I do?",
    "Old habit": "Can I block the card on the system without the form?",
    "Swahili": "Mteja amepoteza kadi, nifanye nini?",
    "Business account": "What documents for a business account?",
    "Workaround": "Can I block now and get the form signed tomorrow?",
    "Not in library": "How do I deposit a foreign currency cheque?",
    "Customer data": "Customer account 01523344556 lost his card, what next?",
    "Leave": "How early must I apply for annual leave?",
}

library = k.load_library()
circulars = sorted({(s.circular, s.title) for s in library})


@st.cache_resource
def retriever():
    return k.get_retriever()

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Kamilisha")
    st.caption("Mfano Bank (fictional) · staff assistant · pilot")
    branch = st.selectbox("Branch", ["Pilot 1", "Pilot 2"])
    role = st.selectbox("Role", ["Teller", "Customer service officer", "Relationship officer", "Branch manager"])
    st.divider()
    st.markdown("**Library (Live versions)**")
    for s in sorted({(s.circular, s.title, s.version, s.effective) for s in library if s.status == "Live"}):
        st.caption(f"{s[0]} · {s[1]} · v{s[2]} · from {s[3]:%d %b %Y}")
    st.divider()
    st.markdown("**Switch-off (Data Management Office)**")
    paused = [c for c, t in circulars if st.toggle(f"Pause {t}", key=f"pause-{c}")]
    st.divider()
    st.markdown("**Search**")
    st.caption(retriever().name)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("No API key found. Add ANTHROPIC_API_KEY to the .env file (see README).")

tab_ask, tab_log = st.tabs(["Ask", "Question log (training unit)"])

# ---------------------------------------------------------------- ask
with tab_ask:
    st.markdown("#### Ask about a procedure or staff policy")
    cols = st.columns(4)
    for i, (label, q) in enumerate(EXAMPLES.items()):
        if cols[i % 4].button(label, width="stretch"):
            st.session_state["q"] = q
    question = st.text_input("Your question (English or Swahili). Do not enter customer details.", key="q")
    if st.button("Ask Kamilisha", type="primary") and question.strip():
        with st.spinner("Checking the current circulars..."):
            st.session_state["ans"] = k.ask(question, branch=branch, role=role, retriever=retriever(),
                                             library=library, paused=paused)
            st.session_state["fb"] = False

    ans = st.session_state.get("ans")
    if ans:
        if ans.masked:
            st.warning(f"Please don't enter customer details. Removed before processing: {', '.join(ans.masked)}.")
        if ans.status == "not_found":
            st.info(ans.not_found_text)
        elif ans.status == "need_info":
            st.info(ans.clarifying_question)
            for o in ans.options:
                st.markdown(f"- {o}")
        else:
            if ans.status == "declined":
                st.error("I can't help with skipping or changing a control. The current rule is:")
            for circ, eff in ans.changed:
                st.warning(f"Changed on {eff.day} {eff:%b %Y}: {circ}. Habit may follow the old version.")
            for i, step in enumerate(ans.steps, 1):
                if step.control:
                    st.markdown(f"**{i}. {step.text}** :red-background[CONTROL]")
                    with st.expander("Circular wording"):
                        st.write(step.section.text)
                        st.caption(step.section.citation)
                else:
                    st.markdown(f"{i}. {step.text}")
            st.caption("Source: " + " · ".join(ans.citations))
        if ans.retrieved:
            with st.expander(f"Sections retrieved ({len(ans.retrieved)}) · {ans.retriever}"):
                for sec, score in ans.retrieved:
                    st.caption(f"{score:.3f} · {sec.citation} · {sec.heading}")
                if ans.controls_added:
                    st.markdown("**Control sections added (G-13)**")
                    for sec in ans.controls_added:
                        st.caption(f"{sec.citation} · {sec.heading}")
                if ans.steps_added:
                    st.markdown("**Procedure steps added**")
                    for sec in ans.steps_added:
                        st.caption(f"{sec.citation} · {sec.heading}")
        if ans.note:
            st.caption(ans.note)
        if st.session_state.get("fb"):
            st.success("Thank you. Sent to the procedure owner.")
        elif st.button("Wrong or unclear"):
            k.write_feedback(ans, branch)
            st.session_state["fb"] = True
            st.rerun()

# ---------------------------------------------------------------- question log
with tab_log:
    path = os.path.join(k.LOG_DIR, "question_log.csv")
    if not os.path.exists(path):
        st.info("No questions logged yet.")
    else:
        log = pd.read_csv(path).fillna("")
        st.caption("Branch and procedure only, never staff names (guardrail G-12).")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Questions", len(log))
        c2.metric("Answered", int((log["status"] == "answered").sum()))
        c3.metric("Not found", int((log["status"] == "not_found").sum()))
        c4.metric("Declined", int((log["status"] == "declined").sum()))
        log["procedure"] = log["circulars_cited"].str.extract(r"^([A-Z]+-[A-Z]+-\d+)")[0].fillna("None")
        st.markdown("**Questions by procedure and branch**")
        st.dataframe(log.pivot_table(index="procedure", columns="branch", values="question_masked",
                                     aggfunc="count", fill_value=0), width="stretch")
        st.markdown("**Latest questions**")
        st.dataframe(log[["timestamp", "branch", "language", "question_masked", "status", "circulars_cited"]]
                     .iloc[::-1], width="stretch", hide_index=True)
