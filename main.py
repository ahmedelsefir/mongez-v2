import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.genai as genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Mongez AI - Professional Mentor",
    version="1.0.0",
    description="A high-performance AI mentor for Programming and English Mastery."
)

# 2. Configure CORS
# Allows your frontend (when you buy the domain) to communicate with this server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[], # TODO: Configure this with your frontend domain for production (e.g., ["https://your-frontend.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Direct Gemini API Configuration
# We use your validated API key directly to ensure 100% connectivity.
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")


# 4. Mongez Personality Setup (System Instructions)
SYSTEM_PROMPT = (
    "You are 'Mongez', an elite Personal Mentor. "
    "Your core objectives are: "
    "1. PROGRAMMING: Teach Python, JavaScript, and TypeScript with clean code examples. "
    "2. ENGLISH: Correct the user's grammar and provide professional vocabulary tips. "
    "3. EXPLANATION: Use Arabic for conceptual explanations, but keep all code and technical terms in English. "
    "4. TONE: Be encouraging, professional, and focus on career growth."
)

# Initialize the Gemini Model
client = genai.Client()
model_id = 'gemini-2.0-flash'

# 5. Data Structures
class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

# 6. API Endpoints
@app.get("/", tags=["Status"])
async def check_health():
    """Returns the current status of the Mongez server."""
    return {
        "status": "online",
        "mentor": "Mongez AI",
        "system": "Active"
    }

@app.post("/chat", response_model=ChatResponse, tags=["Mentorship"])
async def ask_mongez(request: ChatRequest):
    """Sends user queries to the AI and returns the mentor's response."""
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Please provide a message.")
    
    try:
        # Generate response from the AI model
        contents = [
            types.Content(
                role='user',
                parts=[
                    types.Part(
                        text=SYSTEM_PROMPT
                    ),
                    types.Part(
                        text=request.prompt
                    )
                ]
            )
        ]
        result = client.models.generate_content(model=model_id, contents=request.prompt)
        return ChatResponse(response=result.text)
    
    except Exception as e:
        # Log and return server errors
        print(f"Server Side Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Gemini API is busy or key is invalid.")
