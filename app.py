"""
Personal Health Coach - AI-Powered Health Recommendations
========================================================
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime
import traceback

import streamlit as st
import pdfplumber

# Google Gemini (NEW SDK)
from google import genai

# Optional ScaleDown compression
sys.path.append(os.getcwd())
try:
    from scaledown.compressor.scaledown_compressor import ScaleDownCompressor
except ImportError:
    ScaleDownCompressor = None


# =============================================================================
# CONFIG
# =============================================================================

PAGE_CONFIG = {
    "page_title": "Personal Health Coach",
    "page_icon": "🏥",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

HEALTH_COACH_SYSTEM_PROMPT = """
You are an AI Health Coach.

Rules:
- Educational guidance only
- No diagnosis or prescriptions
- Always recommend consulting a doctor
- Be empathetic and clear
- Base advice on WHO / CDC / AHA guidance

Response format:
- Key insights
- Actionable recommendations
- Warning signs
- When to see a doctor
"""


# =============================================================================
# SESSION STATE
# =============================================================================

def initialize_session_state():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("medical_context", "")
    st.session_state.setdefault("compressed_context", "")
    st.session_state.setdefault("wellness_goals", "")


# =============================================================================
# PDF EXTRACTION
# =============================================================================

def extract_medical_data(uploaded_file) -> str:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = []
            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"[Page {i}] {page_text}")
        return " ".join(" ".join(text).split())
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return ""


# =============================================================================
# OPTIONAL COMPRESSION
# =============================================================================

def compress_health_context(text: str) -> str:
    if not text or ScaleDownCompressor is None:
        return text

    try:
        compressor = ScaleDownCompressor(
            api_key=st.secrets["SCALEDOWN_API_KEY"]
        )
        return compressor.compress(
            context=text,
            prompt="Extract key vitals, conditions, meds, labs.",
            target_model="gemini-2.5-flash",
            ratio=0.4
        )
    except Exception:
        return text


# =============================================================================
# GEMINI HEALTH ADVICE (CORRECT USAGE)
# =============================================================================

def get_health_advice(
    user_query: str,
    medical_text: str,
    goals: str,
    chat_history: List[Dict[str, str]]
) -> str:

    try:
        if "GEMINI_API_KEY" not in st.secrets:
            return "❌ GEMINI_API_KEY missing."

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in chat_history[-6:]
        )

        full_prompt = f"""
{HEALTH_COACH_SYSTEM_PROMPT}

Medical Records:
{medical_text or "None provided"}

Wellness Goals:
{goals or "None provided"}

Conversation History:
{history_text}

User Question:
{user_query}

Provide safe, evidence-based health guidance.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        return response.text

    except Exception as e:
        return f"❌ Gemini error:\n{e}"


# =============================================================================
# UI
# =============================================================================

def render_sidebar():
    with st.sidebar:
        st.title("🏥 Health Profile")

        uploaded_file = st.file_uploader(
            "Upload medical PDF",
            type=["pdf"]
        )

        if uploaded_file:
            text = extract_medical_data(uploaded_file)
            compressed = compress_health_context(text)
            st.session_state.medical_context = text
            st.session_state.compressed_context = compressed
            st.success("Medical record loaded")

        st.session_state.wellness_goals = st.text_area(
            "Wellness goals / symptoms",
            height=120
        )

        st.warning(
            "⚠️ This app provides educational information only. "
            "Always consult a healthcare professional."
        )


def render_chat():
    st.title("💬 Personal Health Coach")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a health question..."):
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your health data..."):
                reply = get_health_advice(
                    prompt,
                    st.session_state.compressed_context
                    or st.session_state.medical_context,
                    st.session_state.wellness_goals,
                    st.session_state.messages
                )
                st.markdown(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )


# =============================================================================
# MAIN
# =============================================================================

def main():
    st.set_page_config(**PAGE_CONFIG)
    initialize_session_state()
    render_sidebar()
    render_chat()

    st.caption(
        f"Session started: {datetime.now():%Y-%m-%d %H:%M}"
    )


if __name__ == "__main__":
    main()
