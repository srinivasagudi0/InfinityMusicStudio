import streamlit as st
from lyric_generator import generate_lyrics


st.title("Infinity Music Studio")
st.set_page_config(page_title="Infinity Music Studio", page_icon=":musical_note:")

st.write("A small music studio where you can create lyrics for a song, adjust the tone, and perform all the necessary tasks from writing to polishing songs before publishing.")

feature = st.selectbox("Select a feature", ["AI-assisted lyric generation", "editing and polishing lyrics"])

if feature == "AI-assisted lyric generation":
    st.header("AI-assisted Lyric Generation")
    theme = st.text_input("Enter a theme or mood for your song and eloborate on the theme if you want to.")
    if st.button("Generate Lyrics"):    
        if theme:
            with st.spinner("Generating lyrics..."):
                lyrics = generate_lyrics(theme)
            st.subheader("Generated Lyrics")
            st.text_area("Your generated lyrics will appear here:", value=lyrics, height=300)
        else:
            st.warning("Please enter a theme or mood to generate lyrics.")

elif feature == "editing and polishing lyrics":
    st.header("Editing and Polishing Lyrics")
    ## add logic for editing and polishing lyrics here
    ####
