from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth import User, user_exists, register_user, authenticate_user
from ai_model import run_query
from typing import Optional
from pydantic import BaseModel
app = FastAPI()

# CORS middleware setup for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://journeybuddy-backend.onrender.com/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryData(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    purposeOfVisit: Optional[str] = None
    numberOfPeople: Optional[str] = None
    withFamily: Optional[str] = None
    gender: Optional[str] = None
    maritalStatus: Optional[str] = None
    foodPreference: Optional[str] = None
    additionalNotes: Optional[str] = None
    locationPreference: Optional[str] = None
    budget: Optional[str] = None
    typeOfStay: Optional[str] = None
    stayPreference: Optional[str] = None
    requiredFacilities: Optional[str] = None

class QnaQuery(BaseModel):
    query: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/register")
def register(user: User):
    if user_exists(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    register_user(user.email, user.password)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: User):
    if authenticate_user(user.email, user.password):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/recommend")
async def recommend(data: QueryData):
    try:
       
        query = f"""
            Hi, my name is {data.name} and I am visiting Ooty with {data.numberOfPeople} people, 
            you have to search for a hotels that can accommodate us. Meaning that should be less than or equal to {data.numberOfPeople} while searching for query.
            the budget is {data.budget}, it can be 1000 above the budget or 1000 below the budget.
            give top 10 matching hit hotel names only.
        """
       
        response = run_query(query)
        print(response)
        return {"message": "Recommendation processed successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/qna")
def qna_endpoint(data: QnaQuery):
    try:
        response = run_query(data.query)
        return {"message": "Query processed successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use environment variable PORT if available, else default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)