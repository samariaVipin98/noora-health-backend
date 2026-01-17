import json
from models.models import Character
from openai import OpenAI
import os
import requests
from typing import Set

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_dialogue_sync(dialogue: str, character: Character):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                      You are a **harsh, highly precise dialogue critic**.

                      Task:
                      - Rate the dialogue ONLY on **Character Voice Accuracy** for both Rick Sanchez and {character.name}.
                      - Use a **1–5 score**, where:
                        - 1 = wildly out of character, very generic or wrong tone
                        - 2 = mostly out of character, a few hints of the right voice
                        - 3 = mixed: some lines fit, many are generic or slightly off
                        - 4 = mostly in character with minor issues
                        - 5 = extremely in character throughout, no major off-notes
                      - **Be very critical and conservative**: if you notice clear issues, choose the **lower** score.

                      Personas to enforce:
                      - Rick Sanchez:
                        - Extremely cynical, jaded, often nihilistic.
                        - Sarcastic, insulting, dark humor, often dismissive or condescending.
                        - Very smart and self-aware, rarely earnest or wholesome for long.
                      - {character.name} (a {character.species}, currently {character.status}):
                        - Should also feel **cynical** or at least sharp/edgy in tone, not flat or generic.
                        - Their lines should reflect their status/context when relevant (e.g., if they are "Dead", darker or more detached reactions make more sense than casual small talk).

                      What to look for:
                      - Flag any lines where **Rick sounds too kind, supportive, naive, bland, or unlike his TV persona**.
                      - Flag any lines where **{character.name} sounds generic, emotionless, or totally ignores their status/species/context**.
                      - Pay special attention to whether both characters **consistently** maintain their cynical tone.

                      Output format (VERY IMPORTANT):
                      - Return **strictly** a JSON object with:
                        - "score": the numeric rating (1–5)
                        - "reason": a **short but specific** explanation
                      - In "reason":
                        - Clearly highlight the **main inaccuracies** or strengths.
                        - Explicitly mention **which character** felt off and **why** (e.g. "Rick is too gentle in early lines", "{character.name} ignores being dead and sounds like a normal person").
                        - Focus only on **persona/voice accuracy**, not grammar or plot.

                      Dialogue to evaluate:
                      \"\"\"{dialogue}\"\"\"
                    """
                }
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Judge Error: {e}")
        return {"score": 0, "reason": "Evaluation Failed"}

def extract_id_from_url(url: str) -> int:
    """Extracts ID from a URL like 'https://rickandmortyapi.com/api/character/1'"""
    if not url: return -1
    return int(url.split("/")[-1])

def get_all_ids_from_endpoint(endpoint_url: str, key: str) -> Set[int]:
    """Fetches an object (Episode/Location) and returns the set of Character IDs inside it."""
    try:
        resp = requests.get(endpoint_url)
        if resp.status_code != 200:
            return set()
        data = resp.json()
        # 'results' list if search, or direct dict if specific ID. 
        # We assume search returns list, take the first match for simplicity.
        item = data['results'][0] if 'results' in data else data
        
        urls = item.get(key, []) # key is either 'characters' or 'residents'
        return {extract_id_from_url(url) for url in urls}
    except:
        return set()