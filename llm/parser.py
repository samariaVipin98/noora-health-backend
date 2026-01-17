import re
from models.models import AgentPayload
from transformers import pipeline

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def parse_intent(query: str) -> AgentPayload:
    payload = AgentPayload()
    q_lower = query.lower()

    # Rule-Based Extraction of the status & species
    if "dead" in q_lower: payload.status = "dead"
    elif "alive" in q_lower: payload.status = "alive"
    elif "unknown" in q_lower: payload.status = "unknown"

    if "alien" in q_lower: payload.species = "alien"
    elif "human" in q_lower: payload.species = "human"

    # Regex Extraction for episode codes like S01E04
    ep_match = re.search(r"(s\d+e\d+)", q_lower)
    if ep_match:
        payload.episode_code = ep_match.group(1).upper()

    # NER Extraction for locations
    ner_results = ner_pipeline(query)
    for entity in ner_results:
        if entity['entity_group'] == 'LOC':
            payload.location_name = entity['word']
            break 
    
    # Fallback: specific fix for "Earth (C-137)" as NER sometimes splits it
    if "earth" in q_lower:
        payload.location_name = "Earth"
        
    return payload