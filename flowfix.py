import json
import os

import streamlit as st
from openai import OpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
flowfix_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def load_last_generated_lyrics():
    try:
        with open("last_generated_lyrics.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def save_last_generated_lyrics(lyrics):
    with open("last_generated_lyrics.txt", "w") as file:
        file.write(lyrics)


def analyze_lyrics_with_openai(text):
    if not text.strip():
        return []

    if not flowfix_client:
        return [
            {
                "id": "no_key",
                "message": "Set OPENAI_API_KEY to get intelligent AI feedback.",
                "revised_lyrics": text,
            }
        ]

    system_prompt = (
        "You are a songwriting coach. Return strict JSON with key 'suggestions'. "
        "Each suggestion must have: id, message, revised_lyrics. "
        "Keep message short. revised_lyrics must preserve user style and only make small improvements. "
        "Give at most 3 suggestions. "
        "Dont chnage the meaning of the lyrics, just make them better. "
        "Focus on improving the last line and the rhyming structure."
    )

    user_prompt = f"Lyrics:\n{text}"

    try:
        response = flowfix_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        raw = response.choices[0].message.content or '{"suggestions":[]}'
        data = json.loads(raw)
        suggestions = data.get("suggestions", [])
        cleaned = []
        for i, suggestion in enumerate(suggestions[:3]):
            cleaned.append(
                {
                    "id": str(suggestion.get("id", f"s{i + 1}")),
                    "message": str(suggestion.get("message", "Suggested improvement")),
                    "revised_lyrics": str(suggestion.get("revised_lyrics", text)),
                }
            )
        return cleaned
    except Exception:
        return [
            {
                "id": "api_error",
                "message": "AI feedback unavailable right now. Try again.",
                "revised_lyrics": text,
            }
        ]


def render_flowfix():
    st.header("FLowfix")
    st.caption("Write lyrics, get instant suggestions, accept or decline any edit.")

    if "flowfix_lyrics" not in st.session_state:
        st.session_state["flowfix_lyrics"] = load_last_generated_lyrics()

    if "flowfix_declined" not in st.session_state:
        st.session_state["flowfix_declined"] = []

    lyrics_input = st.text_area(
        "Write your song lyrics:",
        value=st.session_state["flowfix_lyrics"],
        height=280,
        placeholder="Type your verse here...",
    )

    if lyrics_input != st.session_state["flowfix_lyrics"]:
        st.session_state["flowfix_lyrics"] = lyrics_input
        st.session_state["flowfix_declined"] = []

    suggestions = analyze_lyrics_with_openai(st.session_state["flowfix_lyrics"])
    visible_suggestions = [
        suggestion
        for suggestion in suggestions
        if suggestion["id"] not in st.session_state["flowfix_declined"]
    ]

    st.subheader("Real-time feedback")
    if not st.session_state["flowfix_lyrics"].strip():
        st.info("Start writing to receive suggestions.")
    elif not visible_suggestions:
        st.success("Nice progress. No immediate suggestions right now.")
    else:
        for i, suggestion in enumerate(visible_suggestions):
            st.markdown(f"**Suggestion {i + 1}:** {suggestion['message']}")
            accept_col, decline_col = st.columns(2)

            with accept_col:
                if st.button("Accept", key=f"flowfix_accept_{suggestion['id']}_{i}"):
                    st.session_state["flowfix_lyrics"] = suggestion["revised_lyrics"]
                    save_last_generated_lyrics(st.session_state["flowfix_lyrics"])
                    st.rerun()

            with decline_col:
                if st.button("Decline", key=f"flowfix_decline_{suggestion['id']}_{i}"):
                    st.session_state["flowfix_declined"].append(suggestion["id"])
                    st.rerun()
