import streamlit as st
import datetime
import os
import uuid
import pandas as pd

from logic.model_utils import get_model, get_vectorizer, get_vocab
from logic.text_utils import clean_text, get_confidence
from logic.style_utils import load_css, render_message_html

# Load model, vectorizer, vocab
model = get_model()
vectorizer = get_vectorizer()
vocab = get_vocab()

# Initialize session state
if "accepted_disclaimer" not in st.session_state:
    st.session_state.accepted_disclaimer = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Disclaimer gate
if not st.session_state.accepted_disclaimer:
    st.set_page_config(page_title="🚨 Disclaimer")
    st.title("🚨 Responsible Use Disclaimer")

    st.markdown("""
    This app uses machine learning to detect toxic or harmful content in user messages.

    It is intended **solely for educational and cybersecurity demonstration purposes**. This is **not a censorship platform**, and model predictions may not be perfect.

    By continuing, you agree to use this app responsibly and not to deliberately submit harmful, illegal, or offensive content.
    """)

    agree = st.checkbox("I have read and agree to use this tool responsibly.")
    if st.button("Enter Application", disabled=not agree):
        st.session_state.accepted_disclaimer = True
        st.rerun()
    st.stop()

# App layout
st.set_page_config(page_title="AI Moderator", layout="wide")
st.title("🤖 AI-Powered Moderated Bulletin Board")
tab1, tab2, tab3 = st.tabs(["📋 Bulletin Board", "🚨 Toxic Word Log", "📈 Improve the Model"])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("📨 Post a Message")
    with st.form("message_form"):
        message = st.text_area("Type your message here...")
        submitted = st.form_submit_button("📨 Post")

    if submitted and message.strip():
        cleaned = clean_text(message)
        vect = vectorizer.transform([cleaned])
        prediction = model.predict(vect)[0]
        confidence = get_confidence(model, vect)

        st.session_state.messages.append({
            "user": "Anonymous",
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_toxic": prediction,
            "confidence": confidence
        })

    # Render messages
    st.markdown(load_css(), unsafe_allow_html=True)
    board_html = '<div class="message-board">'
    for msg in reversed(st.session_state.messages[-3:]):
        board_html += render_message_html(msg)
    board_html += '</div>'
    st.markdown(board_html, unsafe_allow_html=True)

    # Expander for older messages
    older_msgs = st.session_state.messages[:-3]
    if older_msgs:
        with st.expander("📂 View older messages"):
            for msg in reversed(older_msgs):
                st.markdown(render_message_html(msg), unsafe_allow_html=True)

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("🚨 Toxic Word Log")
    st.caption("Flagged words from moderated messages, with the model's confidence in each prediction.")

    toxic_log = []
    for msg in st.session_state.messages:
        if msg["is_toxic"]:
            cleaned = clean_text(msg["message"])
            words = cleaned.split()
            vect = vectorizer.transform([cleaned])
            indices = vect.nonzero()[1]
            toxic_words = [vocab[i] for i in indices if vocab[i] in words]
            conf = get_confidence(model, vect)

            toxic_log.append({
                "User": msg.get("user", "Anonymous"),
                "Flagged Words": ", ".join(sorted(set(toxic_words))),
                "Confidence (%)": f"{conf:.2f}" if conf is not None else "N/A",
                "Timestamp": msg["timestamp"]
            })

    if toxic_log:
        st.dataframe(pd.DataFrame(toxic_log), use_container_width=True)
    else:
        st.info("No toxic messages have been flagged yet.")

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("📈 Help Improve the AI Moderator")
    st.markdown("If a toxic message was missed, submit it here to help us retrain the model.")

    phrase = st.text_area("Enter a word or phrase that should be flagged:")
    labels = st.multiselect(
        "Choose at least one toxic category:",
        ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    )
    submit = st.button("💾 Submit for Retraining")

    if submit:
        if not phrase.strip():
            st.warning("Please enter a phrase.")
        elif len(labels) == 0:
            st.warning("Please select at least one category.")
        else:
            entry = {
                "id": uuid.uuid4().hex[:8],
                "comment_text": phrase.strip(),
                "toxic": 0,
                "severe_toxic": 0,
                "obscene": 0,
                "threat": 0,
                "insult": 0,
                "identity_hate": 0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            for label in labels:
                entry[label] = 1

            df = pd.DataFrame([entry])
            path = "retrain.csv"
            if os.path.exists(path):
                df.to_csv(path, mode='a', header=False, index=False)
            else:
                df.to_csv(path, index=False)

            st.success(f"✅ Entry saved with ID `{entry['id']}` to retrain.csv")
