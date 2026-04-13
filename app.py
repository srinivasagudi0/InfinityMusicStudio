import streamlit as st

from auth import authenticate_user, register_user
from lyric_generator import generate_lyrics
from edit_polish import polish_song_lyrics as edit_polish
from flowfix import render_flowfix
from profile import render_profile
from spotify import render_spotify, render_spotify_background_player
from structure_editor import structure_editor
from tone_style import correct_tone_and_style as cts


st.set_page_config(page_title="Infinity Music Studio", page_icon=":musical_note:")
st.title("Infinity Music Studio")


def render_download_button(lyrics, file_name, key):
    if lyrics:
        st.download_button("Download Lyrics", lyrics, file_name=file_name, key=key)


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["authenticated"]:
    st.subheader("Login")
    auth_mode = st.radio("Choose an option", ["Login", "Register"], horizontal=True)

    if auth_mode == "Login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")

        if login_submitted:
            if authenticate_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    else:
        with st.form("register_form"):
            username = st.text_input("Create a username")
            password = st.text_input("Create a password", type="password")
            register_submitted = st.form_submit_button("Register")

        if register_submitted:
            if not username or not password:
                st.warning("Enter a username and password.")
            elif register_user(username, password):
                st.success("Account created. You can log in now.")
            else:
                st.error("That username already exists.")

    st.stop()

logout_col, welcome_col = st.columns([1, 4])

with logout_col:
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()

with welcome_col:
    st.caption(f"Logged in as {st.session_state['username']}")

st.write("A small music studio where you can create lyrics for a song, adjust the tone, and perform all the necessary tasks from writing to polishing songs before publishing.")

feature = st.selectbox("Select a feature", ["AI-assisted lyric generation", "editing and polishing lyrics", "structure editing", "FLowfix- Flagship", "tone & style adjustment", "Spotify", "Profile"])

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
            render_download_button(lyrics, "last_generated_lyrics.txt", "download_generated_lyrics")
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
    render_download_button(st.session_state["last_lyrics"], "edited_lyrics.txt", "download_editing_current_lyrics")
    change = st.text_input("How would you like to change the lyrics? (e.g., make it more poetic, change the tone, etc.)")
    if st.button("Polish Lyrics"):
        if st.session_state["last_lyrics"] and change:
            with st.spinner("Polishing lyrics..."):
                polished_lyrics = edit_polish(st.session_state["last_lyrics"])
            st.subheader("Polished Lyrics")
            st.text_area("Your polished lyrics will appear here:", value=polished_lyrics, height=300)
            render_download_button(polished_lyrics, "polished_lyrics.txt", "download_polished_lyrics")
        else:
            st.warning("Please enter the lyrics you want to polish and how you want to change them.")

elif feature == "structure editing":
    st.header("Structure Editing")
    if "last_lyrics" not in st.session_state:
        st.session_state["last_lyrics"] = ""
        try:
            with open("last_generated_lyrics.txt", "r") as file:
                st.session_state["last_lyrics"] = file.read()
        except FileNotFoundError:
            st.warning("No previously generated lyrics found. Please generate lyrics first.")
    st.text_area("Your current lyrics:", value=st.session_state["last_lyrics"], height=300)
    render_download_button(st.session_state["last_lyrics"], "current_lyrics.txt", "download_structure_current_lyrics")
    structure_change = st.text_input("How would you like to change the structure of the song? (e.g., change the order of verses and chorus, add a bridge, etc.)")
    if st.button("Edit Structure"):
        if st.session_state["last_lyrics"] and structure_change:
            with st.spinner("Editing song structure..."):
                edited_lyrics = structure_editor(st.session_state["last_lyrics"], structure_change)
            st.subheader("Edited Lyrics with New Structure")
            st.text_area("Your edited lyrics will appear here:", value=edited_lyrics, height=300)
            render_download_button(edited_lyrics, "structured_lyrics.txt", "download_structured_lyrics")
        else:
            st.warning("Please enter the lyrics you want to edit and how you want to change the structure.")

elif feature == "FLowfix- Flagship":
    render_flowfix()

elif feature == "tone & style adjustment":
    st.header("Tone & Style Adjustment")
    if "last_lyrics" not in st.session_state:
        st.session_state["last_lyrics"] = ""
        try:
            with open("last_generated_lyrics.txt", "r") as file:
                st.session_state["last_lyrics"] = file.read()
        except FileNotFoundError:
            st.warning("No previously generated lyrics found. Please generate lyrics first.")
    genre = st.selectbox("Select the genre of your song:", ["Pop", "Rock", "Hip-Hop", "Country", "Jazz", "Other"])
    mood = st.selectbox("Select the mood of your song:", ["Happy", "Sad", "Angry", "Romantic", "Energetic", "Other"])
    formality_slider = st.slider("Select the formality level of your lyrics:", 0, 10, 2)
    rephrase = st.text_input("How would you like to change the tone and style of your lyrics? (e.g., make it more formal, change the genre, etc.)")
    if st.button("Adjust Tone & Style"):
        if st.session_state["last_lyrics"] and rephrase:
            with st.spinner("Adjusting tone and style..."):
                desired_change = f"Genre: {genre}, Mood: {mood}, Formality: {formality_slider}/10. {rephrase}"
                adjusted_lyrics = cts(st.session_state["last_lyrics"], desired_change)
            st.subheader("Adjusted Lyrics")
            st.text_area("Your adjusted lyrics will appear here:", value=adjusted_lyrics, height=300)
            render_download_button(adjusted_lyrics, "adjusted_lyrics.txt", "download_adjusted_lyrics")
        else:
            st.warning("Please enter the lyrics you want to adjust and how you want to change the tone and style.")

elif feature == "Spotify":
    render_spotify()


elif feature == "Profile":
    render_profile(st.session_state["username"])
    if st.button("My songs"):
        pass


render_spotify_background_player()
