import streamlit as st


st.title("Infinity Music Studio")
st.set_page_config(page_title="Infinity Music Studio", page_icon=":musical_note:")

st.write("A small music studio where you can create lyrics for a song, adjust the tone, and perform all the necessary tasks from writing to polishing songs before publishing.")

feature = st.selectbox("Select a feature", ["AI-assisted lyric generation"])

if feature == "AI-assisted lyric generation":
    st.header("AI-assisted Lyric Generation")
    # call the function to generate lyrics here
    ###
