import sqlite3

import streamlit as st


DB_FILE = "users.db"


def open_db():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = open_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            lyrics TEXT NOT NULL,
            genre TEXT,
            mood TEXT,
            status TEXT DEFAULT 'Draft',
            created_on TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_on TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    conn.commit()
    conn.close()


def get_user_id(username):
    conn = open_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None


def save_song(username, title, lyrics, genre, mood, status):
    user_id = get_user_id(username)
    if user_id is None:
        return False

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO songs (user_id, title, lyrics, genre, mood, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, title.strip(), lyrics.strip(), genre.strip(), mood.strip(), status.strip()),
    )
    conn.commit()
    conn.close()
    return True


def get_user_songs(username):
    user_id = get_user_id(username)
    if user_id is None:
        return []

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, genre, mood, status, created_on, updated_on
        FROM songs
        WHERE user_id = ?
        ORDER BY updated_on DESC, id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    songs = []
    for row in rows:
        songs.append(
            {
                "id": row[0],
                "title": row[1],
                "genre": row[2] or "",
                "mood": row[3] or "",
                "status": row[4] or "Draft",
                "created_on": row[5] or "",
                "updated_on": row[6] or "",
            }
        )
    return songs


def get_song(song_id, username):
    user_id = get_user_id(username)
    if user_id is None:
        return None

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, lyrics, genre, mood, status, created_on, updated_on
        FROM songs
        WHERE id = ? AND user_id = ?
        """,
        (song_id, user_id),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "lyrics": row[2],
        "genre": row[3] or "",
        "mood": row[4] or "",
        "status": row[5] or "Draft",
        "created_on": row[6] or "",
        "updated_on": row[7] or "",
    }


def update_song(song_id, username, title, lyrics, genre, mood, status):
    user_id = get_user_id(username)
    if user_id is None:
        return False

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE songs
        SET title = ?, lyrics = ?, genre = ?, mood = ?, status = ?, updated_on = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (title.strip(), lyrics.strip(), genre.strip(), mood.strip(), status.strip(), song_id, user_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_song(song_id, username):
    user_id = get_user_id(username)
    if user_id is None:
        return False

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM songs WHERE id = ? AND user_id = ?",
        (song_id, user_id),
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def format_song_name(song_id, songs):
    if song_id == 0:
        return "New song"

    for song in songs:
        if song["id"] == song_id:
            return f"{song['title']} ({song['status']})"

    return "Song"


def render_my_songs(username):
    init_db()

    if not username:
        st.error("Please log in first.")
        return

    songs = get_user_songs(username)

    st.header("My Songs")
    st.caption(f"Logged in as {username}")

    count_col, text_col = st.columns([1, 2])

    with count_col:
        st.metric("Saved songs", len(songs))

    with text_col:
        st.write("Save your lyrics here, open them later, and keep your drafts in one place.")

    song_options = [0] + [song["id"] for song in songs]
    selected_song_id = st.selectbox(
        "Open a song",
        song_options,
        format_func=lambda song_id: format_song_name(song_id, songs),
    )

    current_song = None
    if selected_song_id != 0:
        current_song = get_song(selected_song_id, username)

    default_title = current_song["title"] if current_song else ""
    default_genre = current_song["genre"] if current_song else ""
    default_mood = current_song["mood"] if current_song else ""
    default_status = current_song["status"] if current_song else "Draft"
    default_lyrics = current_song["lyrics"] if current_song else st.session_state.get("last_lyrics", "")

    if not current_song and default_lyrics:
        st.caption("Your latest lyrics are already loaded into this new song form.")

    with st.form("my_songs_form"):
        title = st.text_input("Song title", value=default_title)
        genre = st.text_input("Genre", value=default_genre)
        mood = st.text_input("Mood", value=default_mood)
        status = st.selectbox(
            "Status",
            ["Draft", "Finished"],
            index=0 if default_status == "Draft" else 1,
        )
        lyrics = st.text_area("Lyrics", value=default_lyrics, height=280)
        submitted = st.form_submit_button("Save song")

    if submitted:
        if not title.strip():
            st.warning("Please add a song title.")
        elif not lyrics.strip():
            st.warning("Please add some lyrics first.")
        else:
            if current_song:
                update_song(current_song["id"], username, title, lyrics, genre, mood, status)
                st.success("Song updated.")
            else:
                save_song(username, title, lyrics, genre, mood, status)
                st.success("Song saved.")
            st.rerun()

    if current_song:
        if st.button("Delete this song"):
            delete_song(current_song["id"], username)
            st.success("Song deleted.")
            st.rerun()

    st.subheader("Your Library")

    if songs:
        for song in songs:
            st.write(f"**{song['title']}**")
            st.caption(
                f"{song['status']} | {song['genre'] or 'No genre'} | "
                f"{song['mood'] or 'No mood'} | Updated {song['updated_on'][:10]}"
            )
    else:
        st.info("You do not have any saved songs yet.")


init_db()
