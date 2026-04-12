from openai import OpenAI
import os

def generate_lyrics(prompt):
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Generate lyrics using the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates song lyrics based on a given prompt. Minimum song should be one minute if not mentioned."},
            {"role": "user", "content": f"Generate lyrics for a song with the following theme: {prompt}"}
        ],
        max_tokens=500,
        temperature=0.7,
    )

    # Extract the generated lyrics from the response
    lyrics = response.choices[0].message.content.strip()
    with open("last_generated_lyrics.txt", "w") as f:
        f.write(lyrics)

    return lyrics

