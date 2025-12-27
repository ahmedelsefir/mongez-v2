import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI app
app = FastAPI(title="Mongez AI - Personal Mentor")

# 2. Enable CORS for Frontend (index.html) connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Secure API Key Setup (Using environment variables)
# It's recommended to load API keys from environment variables for security.
# You can set it like: export GOOGLE_API_KEY="your_api_key_here"
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)

# Defining the "Personality" of Mongez AI
SYSTEM_INSTRUCTION = (
    "You are 'Mongez', a high-level Personal Mentor. Your goals are:\n"
    "1. Teach Programming: Explain code concepts (Python, JS, TS) step-by-step with clean examples.\n"
    "2. English Mastery: Correct the user's English mistakes politely and teach technical vocabulary.\n"
    "3. Interaction Style: Be professional, encouraging, and always provide actionable advice.\n"
    "4. Language: Respond in Arabic for explanations, but keep code and technical terms in English."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# 4. Data Models
class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

# 5. API Endpoints
@app.get("/")
async def root():
    return {"status": "Mongez AI is online", "mentor_mode": "Active"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured on server.")
    
    try:
        # Generate response from Gemini
        response = model.generate_content(request.prompt)
        return ChatResponse(response=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run this: uvicorn main:app --host 0.0.0.0 --port 8000 --reload