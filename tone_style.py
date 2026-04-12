from openai import OpenAI
import os

def correct_tone_and_style(lyrics: str, desired_change: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt = (
        "You are a songwriting coach. Adjust the tone and style of the lyrics based on the desired change. Keep the meaning of the lyrics intact while making the necessary adjustments. "
        "Return only the revised lyrics without any explanations."
    )
    user_prompt = f"Lyrics:\n{lyrics}\n\nDesired Change:\n{desired_change}"
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        revised_lyrics = res.choices[0].message.content or lyrics
        return revised_lyrics.strip()
    except Exception:
        return lyrics
    
