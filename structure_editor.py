import os
from openai import OpenAI

def structure_editor(lyrics, structure_change):
    client = OpenAI()
    prompt = f"Here are the original lyrics:\n{lyrics}\n\nPlease change the structure of the song as follows: {structure_change}. Provide the modified lyrics with the new structure."
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that edits song structures. Dont change the lyrics, just the structure of the song."},
            {"role": "user", "content": prompt}
        ]
    )
    
    edited_lyrics = response.choices[0].message.content.strip()
    return edited_lyrics
