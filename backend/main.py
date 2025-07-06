from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import json
import os
from typing import List, Dict, Optional
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Configure CORS to allow requests from React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_query: str
    system_prompt: str = "You are a helpful AI assistant."
    chat_history: Optional[List[ChatMessage]] = []

class ContextManager:
    """Manages chat context and history for better conversations"""
    
    def __init__(self, max_history_length: int = 10):
        self.max_history_length = max_history_length
    
    def prepare_messages(self, request: ChatRequest) -> List[Dict[str, str]]:
        """Prepare messages for Groq API with context awareness"""
        messages = [{"role": "system", "content": request.system_prompt}]
        
        # Add recent chat history (limit to prevent token overflow)
        if request.chat_history:
            recent_history = request.chat_history[-self.max_history_length:]
            for msg in recent_history:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user query
        messages.append({"role": "user", "content": request.user_query})
        
        return messages

context_manager = ContextManager()

@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "groq_api_configured": bool(os.getenv("GROQ_API_KEY"))}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with streaming support
    """
    try:
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY not configured. Please set it in your .env file."
            )
        
        # Prepare messages with context
        messages = context_manager.prepare_messages(request)
        
        # Make streaming request to Groq
        def generate_response():
            try:
                stream = groq_client.chat.completions.create(
                    model="mixtral-8x7b-32768",  # You can change this to other models
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=1,
                    stream=True,
                    stop=None,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        # Format as Server-Sent Events
                        chunk_data = {
                            "choices": [{
                                "delta": {
                                    "content": chunk.choices[0].delta.content
                                }
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_data = {
                    "error": {
                        "message": str(e),
                        "type": "groq_api_error"
                    }
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/chat-simple")
async def chat_simple(request: ChatRequest):
    """
    Non-streaming chat endpoint for testing
    """
    try:
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY not configured. Please set it in your .env file."
            )
        
        messages = context_manager.prepare_messages(request)
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": "mixtral-8x7b-32768",
            "usage": response.usage._asdict() if response.usage else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)