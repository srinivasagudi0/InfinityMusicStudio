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
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            city TEXT,
            favorite_genre TEXT,
            bio TEXT,
            joined_on TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    conn.commit()
    conn.close()


def make_default_profile(username):
    readable_name = username.replace("_", " ").replace(".", " ").strip().title()
    if not readable_name:
        readable_name = "New Artist"

    return {
        "full_name": readable_name,
        "artist_name": readable_name,
        "city": "",
        "favorite_genre": "Pop",
        "bio": "I love writing songs and turning ideas into music.",
    }


def get_user_id(username):
    conn = open_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None


def ensure_profile(username):
    user_id = get_user_id(username)
    if user_id is None:
        return None

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        profile = make_default_profile(username)
        cursor.execute(
            """
            INSERT INTO profiles (user_id, full_name, artist_name, city, favorite_genre, bio)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                profile["full_name"],
                profile["artist_name"],
                profile["city"],
                profile["favorite_genre"],
                profile["bio"],
            ),
        )
        conn.commit()

    conn.close()
    return user_id


def get_profile(username):
    init_db()
    user_id = ensure_profile(username)
    if user_id is None:
        return None

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT users.username, profiles.full_name, profiles.artist_name, profiles.city,
               profiles.favorite_genre, profiles.bio, profiles.joined_on
        FROM profiles
        JOIN users ON users.id = profiles.user_id
        WHERE profiles.user_id = ?
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "username": row[0],
        "full_name": row[1],
        "artist_name": row[2],
        "city": row[3] or "",
        "favorite_genre": row[4] or "",
        "bio": row[5] or "",
        "joined_on": row[6] or "",
    }


def save_profile(username, full_name, artist_name, city, favorite_genre, bio):
    init_db()
    user_id = ensure_profile(username)
    if user_id is None:
        return False

    conn = open_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE profiles
        SET full_name = ?, artist_name = ?, city = ?, favorite_genre = ?, bio = ?
        WHERE user_id = ?
        """,
        (full_name.strip(), artist_name.strip(), city.strip(), favorite_genre.strip(), bio.strip(), user_id),
    )
    conn.commit()
    conn.close()
    return True


def get_profile_completion(profile):
    filled_items = [
        profile["full_name"],
        profile["artist_name"],
        profile["city"],
        profile["favorite_genre"],
        profile["bio"],
    ]
    total_filled = sum(1 for item in filled_items if item.strip())
    return int((total_filled / len(filled_items)) * 100)


def render_profile(username):
    profile = get_profile(username)

    if profile is None:
        st.error("We could not find this user in the database yet.")
        return

    st.header("Your Profile")
    st.caption(f"Username: {profile['username']}")

    completion = get_profile_completion(profile)
    left_col, right_col = st.columns(2)

    with left_col:
        st.metric("Profile complete", f"{completion}%")

    with right_col:
        st.metric("Joined", profile["joined_on"][:10] if profile["joined_on"] else "Today")

    with st.form("profile_form"):
        full_name = st.text_input("Full name", value=profile["full_name"])
        artist_name = st.text_input("Artist name", value=profile["artist_name"])
        city = st.text_input("City", value=profile["city"])
        favorite_genre = st.text_input("Favorite genre", value=profile["favorite_genre"])
        bio = st.text_area("Short bio", value=profile["bio"], height=120)
        submitted = st.form_submit_button("Save profile")

    if submitted:
        if not full_name.strip() or not artist_name.strip():
            st.warning("Please add both your full name and artist name.")
        else:
            save_profile(username, full_name, artist_name, city, favorite_genre, bio)
            st.success("Profile saved.")
            st.rerun()

    st.subheader("Profile preview")
    st.write(f"**Name:** {profile['full_name']}")
    st.write(f"**Artist name:** {profile['artist_name']}")
    st.write(f"**City:** {profile['city'] or 'Not added yet'}")
    st.write(f"**Favorite genre:** {profile['favorite_genre'] or 'Not added yet'}")
    st.write(profile["bio"] or "Add a short bio to tell people about your music.")


init_db()
