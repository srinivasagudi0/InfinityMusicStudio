import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import certifi
import streamlit as st
import streamlit.components.v1 as components


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"


def _read_secret(name):
    value = os.getenv(name)
    if value:
        value = value.strip()
        if value:
            return value

    try:
        secret_value = st.secrets.get(name)
    except Exception:
        secret_value = None

    if secret_value:
        secret_value = str(secret_value).strip()
        if secret_value:
            return secret_value

    return None


def _get_spotify_credentials():
    client_id = _read_secret("SPOTIFY_CLIENT_ID")
    client_secret = _read_secret("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None, None
    return client_id, client_secret


def _get_ssl_context():
    return ssl.create_default_context(cafile=certifi.where())


def _read_json_response(request, auth_error_message, network_error_message):
    try:
        with urllib.request.urlopen(request, timeout=10, context=_get_ssl_context()) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed_body = json.loads(error_body)
            spotify_error = parsed_body.get("error")
            error_description = parsed_body.get("error_description")
            if isinstance(spotify_error, dict):
                reason = spotify_error.get("message") or spotify_error.get("status")
            else:
                reason = spotify_error
            if error_description:
                if reason:
                    reason = f"{reason} ({error_description})"
                else:
                    reason = error_description
            if reason:
                raise RuntimeError(f"{auth_error_message} Spotify said: {reason}.") from exc
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"{auth_error_message} HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"{network_error_message} {reason}") from exc


def _get_access_token():
    client_id, client_secret = _get_spotify_credentials()
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to search Spotify.")

    expires_at = st.session_state.get("spotify_token_expires_at", 0)
    cached_token = st.session_state.get("spotify_access_token")
    if cached_token and time.time() < expires_at:
        return cached_token

    token_request_body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    request = urllib.request.Request(
        SPOTIFY_TOKEN_URL,
        data=token_request_body,
        headers={
            "Authorization": f"Basic {basic_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    payload = _read_json_response(
        request,
        "Spotify authentication failed. Check your Spotify API credentials.",
        "Spotify is unavailable right now.",
    )

    access_token = payload.get("access_token")
    expires_in = payload.get("expires_in", 3600)
    if not access_token:
        raise RuntimeError("Spotify did not return an access token.")

    st.session_state["spotify_access_token"] = access_token
    st.session_state["spotify_token_expires_at"] = time.time() + max(expires_in - 60, 60)
    return access_token


def search_spotify_tracks(query, limit=5):
    access_token = _get_access_token()
    params = urllib.parse.urlencode(
        {
            "q": query,
            "type": "track",
            "limit": limit,
            "market": "US",
        }
    )
    request = urllib.request.Request(
        f"{SPOTIFY_SEARCH_URL}?{params}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )

    payload = _read_json_response(
        request,
        "Spotify search failed.",
        "Spotify is unavailable right now.",
    )

    results = []
    for item in payload.get("tracks", {}).get("items", []):
        results.append(
            {
                "id": item.get("id", ""),
                "name": item.get("name", "Unknown track"),
                "artists": ", ".join(artist.get("name", "") for artist in item.get("artists", [])),
                "album": item.get("album", {}).get("name", ""),
                "external_url": item.get("external_urls", {}).get("spotify", ""),
            }
        )
    return results


def render_spotify():
    st.header("Spotify")
    st.caption("Search for a song, load it, then start playback from the Spotify player below.")

    if "spotify_query" not in st.session_state:
        st.session_state["spotify_query"] = ""

    if "spotify_results" not in st.session_state:
        st.session_state["spotify_results"] = []

    if "spotify_error" not in st.session_state:
        st.session_state["spotify_error"] = ""

    with st.form("spotify_search_form"):
        query = st.text_input(
            "Search for any song",
            value=st.session_state["spotify_query"],
            placeholder="Song title, artist, or both",
        )
        search_submitted = st.form_submit_button("Search Spotify")

    if search_submitted:
        st.session_state["spotify_query"] = query
        st.session_state["spotify_error"] = ""

        if not query.strip():
            st.session_state["spotify_results"] = []
            st.warning("Enter a song name or artist.")
        else:
            try:
                with st.spinner("Searching Spotify..."):
                    st.session_state["spotify_results"] = search_spotify_tracks(query.strip())
            except RuntimeError as exc:
                st.session_state["spotify_results"] = []
                st.session_state["spotify_error"] = str(exc)

    client_id, client_secret = _get_spotify_credentials()

    if st.session_state["spotify_error"]:
        st.error(st.session_state["spotify_error"])

    if st.session_state["spotify_results"]:
        for track in st.session_state["spotify_results"]:
            info_col, play_col = st.columns([5, 1])

            with info_col:
                st.markdown(f"**{track['name']}**")
                st.caption(f"{track['artists']} • {track['album']}")
                if track["external_url"]:
                    st.markdown(f"[Open in Spotify]({track['external_url']})")

            with play_col:
                if st.button("Load", key=f"spotify_load_{track['id']}"):
                    st.session_state["spotify_current_track"] = track
                    st.rerun()
    elif st.session_state["spotify_query"] and not st.session_state["spotify_error"]:
        st.info("No matching songs found.")

    if not client_id or not client_secret:
        st.info("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment or Streamlit secrets to enable Spotify search.")


def render_spotify_background_player():
    current_track = st.session_state.get("spotify_current_track")
    if not current_track or not current_track.get("id"):
        return

    player_col, stop_col = st.columns([5, 1])

    with player_col:
        st.subheader("Spotify Player")
        st.caption(f"{current_track['name']} by {current_track['artists']}")

    with stop_col:
        if st.button("Stop", key="spotify_stop_player"):
            st.session_state.pop("spotify_current_track", None)
            st.rerun()

    st.info("Browsers often block autoplay. If the song does not start on its own, click Play inside the player below.")

    player_html = f"""
    <style>
      body {{
        margin: 0;
        font-family: Arial, sans-serif;
        background: transparent;
        color: white;
      }}
      .spotify-controls {{
        display: flex;
        gap: 8px;
        margin: 0 0 12px 0;
      }}
      .spotify-controls button {{
        border: none;
        border-radius: 999px;
        background: #1db954;
        color: #000;
        cursor: pointer;
        font-weight: 700;
        padding: 10px 16px;
      }}
      .spotify-controls button.secondary {{
        background: #2a2a2a;
        color: #fff;
      }}
      .spotify-status {{
        color: #b3b3b3;
        font-size: 14px;
        margin-bottom: 12px;
      }}
    </style>
    <div class="spotify-controls">
      <button id="spotify-play-button" type="button">Play</button>
      <button id="spotify-pause-button" class="secondary" type="button">Pause</button>
      <button id="spotify-restart-button" class="secondary" type="button">Restart</button>
    </div>
    <div id="spotify-status" class="spotify-status">Loading player...</div>
    <div id="spotify-player"></div>
    <script src="https://open.spotify.com/embed/iframe-api/v1" async></script>
    <script>
      const statusElement = document.getElementById("spotify-status");
      const playButton = document.getElementById("spotify-play-button");
      const pauseButton = document.getElementById("spotify-pause-button");
      const restartButton = document.getElementById("spotify-restart-button");
      let embedController = null;

      const setStatus = (message) => {{
        statusElement.innerText = message;
      }};

      playButton.disabled = true;
      pauseButton.disabled = true;
      restartButton.disabled = true;

      const enableControls = () => {{
        playButton.disabled = false;
        pauseButton.disabled = false;
        restartButton.disabled = false;
      }};

      const bindControls = () => {{
        playButton.onclick = () => {{
          if (!embedController) return;
          try {{
            embedController.resume();
            setStatus("Playing");
          }} catch (error) {{
            setStatus("Play failed. Try the Spotify controls in the embed.");
          }}
        }};

        pauseButton.onclick = () => {{
          if (!embedController) return;
          try {{
            embedController.pause();
            setStatus("Paused");
          }} catch (error) {{
            setStatus("Pause failed.");
          }}
        }};

        restartButton.onclick = () => {{
          if (!embedController) return;
          try {{
            embedController.restart();
            setStatus("Restarted");
          }} catch (error) {{
            setStatus("Restart failed.");
          }}
        }};
      }};

      window.onSpotifyIframeApiReady = (IFrameAPI) => {{
        const element = document.getElementById("spotify-player");
        const options = {{
          uri: "spotify:track:{current_track['id']}",
          width: "100%",
          height: "152",
          theme: 0
        }};

        const callback = (controller) => {{
          embedController = controller;
          enableControls();
          bindControls();
          setStatus("Player ready. Click Play.");

          embedController.addListener("playback_started", () => {{
            setStatus("Playing");
          }});

          embedController.addListener("playback_update", (event) => {{
            if (event?.data?.isPaused) {{
              setStatus("Paused");
            }} else {{
              setStatus("Playing");
            }}
          }});
        }};

        IFrameAPI.createController(element, options, callback);
      }};
    </script>
    """
    components.html(player_html, height=260)

    if current_track.get("external_url"):
        st.markdown(f"[Open in Spotify]({current_track['external_url']})")
