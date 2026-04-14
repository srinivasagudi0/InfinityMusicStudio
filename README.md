# Infinity Music Studio

I built this for myself and fellow begginers who are starting to write, organize, refine songs and have an all in one dedicated place. This is also quite simple to use compared to other software applications I know. 

## Features

This application is also filled with features that simplify the process of making songs. Features include:

- Sign Up / Login - Has authentication so that memory is based on user instead of unified chunk
- My Profile - Personalize your application even more, I love personalization.
- My Songs - Add songs that you wrote and like, so you would never lose them. I added this because normally storing them in Notepad is kind of messy, and you can't specify what type of song using title, mood, genre, and status.
- Lyric Generator (AI-powered) - Generates full songs from simple description.
- Eidt & Polish (AI-powered) - Specifically instructed and hold expertise (joking) in the art of polishing.
- FLowFix - Write the entire song your way while AI watches, understands, and helps in real time. I built FlowFix because I almost never found a tool that truly supports the full songwriting process without taking over. It is not just Grammarly for lyrics, and it is not basic autocorrect. FlowFix follows the meaning, emotion, and direction of the whole song, so the help feels smarter, more natural, and actually useful while you create. This uses gpt-4-mini because it is known for its human like chats.
- Tone & Style editor (AI powered).- Specifically instructed and can change the whole style of the song while preserving meaning.
- Structure Editor (AI-powered) - Worked to improve structure when singing, really important cause the singer needs break and cannot sing all at a time, needs chorus, instruments and more.
- Spotify Integration - I personally like peace music to run in background while working. This is also here to give you quick inspiration.

## Tech Stack
- Python + Streamlit - begginer friendly. Streamlit is also easy to host and has many prebuilt features.
- SQLite - for a local database I set up for storing using and songs (and its metadata).
- OpenAI API - for raw intelligence and its easy integration.
- Spotify API - optional, but cool. It is used for music inspiration or just to have music in the background.

## Project Structure

app.py              # main entry point, handles all page routing and auth flow
auth.py             # login/signup logic with SQLite
db.py               # database setup and queries
lyric_generator.py  # uses GPT-4o to generate lyrics from user inputs
edit_polish.py      # uses GPT-4 to clean up and polish existing lyrics
flowfix.py          # flagship feature — detects and fixes flow/rhythm issues
tone_style.py       # adjusts tone and style of lyrics
structure_editor.py # edits song structure (verse/chorus/bridge)
spotify_integration.py  # pulls Spotify data for context



## AI Integration

Mainly used flagship 4 because it is most human like version OpenAI shipped (in my opinion).
- Lyric Generator → GPT-4o 
- Edit & Polish → GPT-4
- FlowFix → GPT-4o-mini (with structured JSON output)
- Tone & Style → GPT-4o-mini
- Structure Editor → GPT-4


## About
- All logic is written without AI assistance except Spotify integration. THis project is for Remixed (Hack Club YSWS). 

Thanks for reading.
