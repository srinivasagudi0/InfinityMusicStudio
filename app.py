import streamlit as st
from lyric_generator import generate_lyrics
from edit_polish import polish_song_lyrics as edit_polish


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
            st.write("Your genereted lyrics have been saved and you can edit and polish them in the next section.")
        else:
            st.warning("Please enter a theme or mood to generate lyrics.")

elif feature == "editing and polishing lyrics":

    st.header("Editing and Polishing Lyrics")
    if "last_lyrics" not in st.session_state:
        st.session_state["last_lyrics"] = ""
        try:
            with open("last_generated_lyrics.txt", "r") as file:
                st.session_state["last_lyrics"] = file.read()
        except FileNotFoundError:
            st.warning("No previously generated lyrics found. Please generate lyrics first.")

    st.text_area("Edit your lyrics here:", key="last_lyrics", height=300)
    change = st.text_input("How would you like to change the lyrics? (e.g., make it more poetic, change the tone, etc.)")
    if st.button("Polish Lyrics"):
        if st.session_state["last_lyrics"] and change:
            with st.spinner("Polishing lyrics..."):
                polished_lyrics = edit_polish(st.session_state["last_lyrics"])
            st.subheader("Polished Lyrics")
            st.text_area("Your polished lyrics will appear here:", value=polished_lyrics, height=300)
        else:
            st.warning("Please enter the lyrics you want to polish and how you want to change them.")
        
