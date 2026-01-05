import os
import base64
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import google.genai as genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Mongez AI - Professional Mentor v3.0",
    version="3.0.0",
    description="Advanced Multimodal AI Mentor with Vision, Voice, and User Auth."
)

# 2. User Management System (New Update)
# يمكنك إضافة مستخدمين جدد هنا مستقبلاً
USERS = {
    "ahmed": "123",  # المستخدم الأساسي
    "admin": "mongez2026"
}

# 3. Configure CORS (Fixed for Port 8080 responding issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # تم التعديل للسماح بالوصول من أي بورت لحل تعليق الاستجابة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Gemini Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=API_KEY)
model_id = 'gemini-2.0-flash'

# 5. System Personality (Multimodal Instructions)
SYSTEM_PROMPT = (
    "You are 'Mongez', an elite Professional Mentor. "
    "Capabilities: "
    "1. VISION: Analyze uploaded images or code screenshots. "
    "2. VOICE: You can generate speech-ready responses. "
    "3. PROGRAMMING: Expert in Python, JS, and TS. "
    "4. LANGUAGES: Expert English/Arabic tutor. Always explain concepts in Arabic."
)

# 6. Data Structures
class ChatRequest(BaseModel):
    prompt: str
    username: str
    password: str
    image_data: Optional[str] = None  # Base64 string for images (Vision)
    generate_audio: bool = False      # Trigger for Text-to-Speech

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None # For future Audio feature

# 7. Helper Functions
def authenticate_user(username, password):
    if USERS.get(username) == password:
        return True
    return False

# 8. API Endpoints
@app.get("/", tags=["Status"])
async def check_health():
    return {"status": "online", "mentor": "Mongez AI Professional", "version": "3.0"}

@app.post("/chat", response_model=ChatResponse, tags=["Mentorship"])
async def ask_mongez(request: ChatRequest):
    # Check Authentication
    if not authenticate_user(request.username, request.password):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid username or password.")

    try:
        content_parts = [types.Part(text=SYSTEM_PROMPT), types.Part(text=request.prompt)]
        
        # Add Image if provided (Vision Feature)
        if request.image_data:
            image_part = types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=base64.b64decode(request.image_data)
                )
            )
            content_parts.append(image_part)

        # Generate Multimodal Response
        response = client.models.generate_content(
            model=model_id,
            contents=[types.Content(role="user", parts=content_parts)]
        )
        
        return ChatResponse(response=response.text)

    except Exception as e:
        print(f"Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing your request with Gemini 2.0.")

# 9. Run with: streamlit run main.py --server.port 8080
