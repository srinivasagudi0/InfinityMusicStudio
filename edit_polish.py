import os
from openai import OpenAI


def polish_song_lyrics(lyrics):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that polishes song lyrics to make them more poetic and impactful, also how the user likes it to be. DONT make a whole new song, just polish the original one."},
            {"role": "user", "content": f"Please polish the following song lyrics:\n\n{lyrics}"}
        ]
    )
    polished_lyrics = response.choices[0].message.content
    return polished_lyrics
