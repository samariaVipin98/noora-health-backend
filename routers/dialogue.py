from typing import List
from models.models import GenerateRequest
from fastapi import APIRouter, HTTPException
from utils import client, evaluate_dialogue_sync


router = APIRouter(prefix="/dialogue", tags=["dialogue"])

@router.post("/generate")
async def generate_dialogue(req: GenerateRequest):
    char = req.character
    
    prompt = f"""
    Write a short script (2-3 dialogue interactions) between Rick Sanchez and {char.name}.
    KEEP IT NATURAL AND CONVERSATIONAL.

    Context: {char.name} is a {char.species} and is currently {char.status}.
    
    Format:
    Rick: [Line]
    {char.name}: [Line]
    """

    try:
        # 1. Generate Content
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        dialogue = completion.choices[0].message.content
        heuristics = {
            "mentionsName": char.name in dialogue,
            "statusCheck": True
        }
        if char.status == 'Dead':
            # Check for ghost/dead references if character is dead
            lower_d = dialogue.lower()
            if not any(x in lower_d for x in ['dead', 'ghost', 'corpse', 'silent']):
                heuristics['statusCheck'] = False

        rubric = evaluate_dialogue_sync(dialogue, char)

        return {
            "dialogue": dialogue,
            "metrics": {
                "heuristics": heuristics,
                "rubric": rubric
            }
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
