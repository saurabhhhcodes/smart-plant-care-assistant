
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Local imports
from auth import initialize_db, register_user, login_user
from plant_agent import PlantCareAgent
from email_agent import send_welcome_email

# Initialize the database
initialize_db()

app = FastAPI(
    title="Plant Pal AI API",
    description="API for the Plant Pal AI mobile app.",
    version="1.0.0",
)

# --- Pydantic Models for Request and Response Bodies ---

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image string
    provider: str = "openai"
    api_key: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = None
    provider: str = "openai"
    api_key: Optional[str] = None

# --- API Endpoints ---

@app.post("/register", tags=["Authentication"])
def register(user: UserRegistration):
    """Register a new user."""
    success = register_user(user.username, user.email, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    
    # Send a welcome email
    send_welcome_email(user.email, user.username)
    
    return {"message": "User registered successfully."}

@app.post("/login", tags=["Authentication"])
def login(user: UserLogin):
    """Log in a user."""
    success = login_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"message": "Login successful."}

@app.post("/analyze", tags=["Plant Analysis"])
def analyze_plant_image(request: ImageAnalysisRequest):
    """Analyze a plant image and return a health assessment."""
    try:
        agent = PlantCareAgent(api_key=request.api_key, provider=request.provider)
        analysis_result = agent.analyze_image(request.image_data)
        if analysis_result.get('status') == 'error':
            raise HTTPException(status_code=400, detail=analysis_result.get('message'))
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", tags=["Chat"])
def chat_with_agent(request: ChatRequest):
    """Chat with the plant care assistant."""
    try:
        agent = PlantCareAgent(api_key=request.api_key, provider=request.provider)
        response = agent.chat(request.message, request.chat_history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/care-instructions/{plant_type}", tags=["Plant Care"])
def get_care_instructions_for_plant(plant_type: str, provider: str = "openai", api_key: Optional[str] = None):
    """Get care instructions for a specific plant type."""
    try:
        agent = PlantCareAgent(api_key=api_key, provider=provider)
        instructions = agent.get_care_instructions(plant_type)
        return {"plant_type": plant_type, "instructions": instructions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Plant Pal AI API!"}

# --- Main block to run the app ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
