from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import json

router = APIRouter()

class UserPreference(BaseModel):
    locationPreference: str
    budget: int
    typeOfStay: str
    stayPreference: str
    foodPreference: str
    requiredFacilities: List[str]

class Hotel(BaseModel):
    hotelName: str
    attractionsNearby: List[str]
    budget: int
    facilities: List[str]
    reviewStars: int

def load_hotels():
    # Load hotel data from JSON file
    with open("ooty_hotels_facilities_enhanced_data_updated.json", "r") as file:
        hotels = json.load(file)
    return hotels

@router.post("/recommendations/")
def get_recommendations(user_pref: UserPreference) -> List[Hotel]:
    hotels = load_hotels()
    recommended_hotels = []

    for hotel in hotels:
        if user_pref.locationPreference.lower() in (attraction.lower() for attraction in hotel['attractionsNearby']) and \
           hotel['budget'] <= user_pref.budget and \
           all(facility.lower() in (facility.lower() for facility in hotel['facilities']) for facility in user_pref.requiredFacilities):
            recommended_hotels.append(Hotel(**hotel))

    if not recommended_hotels:
        raise HTTPException(status_code=404, detail="No hotels found matching the criteria")

    return recommended_hotels
