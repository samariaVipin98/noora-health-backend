from typing import Optional, Set

import requests
from llm.parser import parse_intent
from models.models import SearchRequest
from fastapi import APIRouter

from utils import get_all_ids_from_endpoint


router = APIRouter(prefix="/search", tags=["search"])


@router.post("")
async def semantic_search(req: SearchRequest):
    plan = parse_intent(req.query)
    if not (plan.status or plan.species or plan.episode_code or plan.location_name):
        return {
            "interpretation": plan,
            "count": 0,
            "results": []
        }

    candidate_ids: Optional[Set[int]] = None

    if plan.episode_code:
        ep_search = requests.get(f"https://rickandmortyapi.com/api/episode/?episode={plan.episode_code}")
        if ep_search.status_code == 200:
            ep_ids = get_all_ids_from_endpoint(ep_search.url, 'characters')
            candidate_ids = ep_ids
        else:
            return {"error": f"Episode {plan.episode_code} not found"}

    if plan.location_name:
        loc_search = requests.get(f"https://rickandmortyapi.com/api/location/?name={plan.location_name}")
        if loc_search.status_code == 200:
            loc_ids = get_all_ids_from_endpoint(loc_search.url, 'residents')
            if candidate_ids is None:
                candidate_ids = loc_ids
            else:
                candidate_ids = candidate_ids.intersection(loc_ids)
        else:
            print(f"Location '{plan.location_name}' not found via API search.")

    final_results = []
    
    if candidate_ids is not None:
        if not candidate_ids:
            return {"message": "No characters found matching intersecting criteria."}
            
        ids_list = list(candidate_ids)
        
        ids_str = str(ids_list).replace(" ","") # format: [1,2,3]
        
        url = f"https://rickandmortyapi.com/api/character/{ids_str}"
        resp = requests.get(url)
        
        data = []
        if resp.status_code == 200:
            json_resp = resp.json()
            data = json_resp if isinstance(json_resp, list) else [json_resp]
            
        for char in data:
            match = True
            if plan.status and char['status'].lower() != plan.status: match = False
            if plan.species and plan.species not in char['species'].lower(): match = False
            
            if match:
                final_results.append(char)

    else:
        params = {}
        if plan.status: params['status'] = plan.status
        if plan.species: params['species'] = plan.species
        
        resp = requests.get("https://rickandmortyapi.com/api/character/", params=params)
        if resp.status_code == 200:
            final_results = resp.json().get('results', [])

    return {
        "interpretation": plan,
        "count": len(final_results),
        "results": [{"id": c['id'], "name": c['name'], "status": c['status'], "location": c['location']['name'], "image": c['image'], "species": c['species']} for c in final_results]
    }