# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from groq import Groq
# import os
# from dotenv import load_dotenv
# from typing import Optional, List, Dict
# import json
# import uuid
# from datetime import datetime
# from pathlib import Path
# import boto3
# from botocore.exceptions import ClientError

# # Load environment variables
# load_dotenv(override=True)

# app = FastAPI()

# # Configure CORS
# origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Groq client
# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

# # Define Model Name
# MODEL_NAME = "openai/gpt-oss-120b"

# # Memory storage configuration (AWS S3 vs Local)
# USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
# S3_BUCKET = os.getenv("S3_BUCKET", "")
# MEMORY_DIR = Path(os.getenv("MEMORY_DIR", "../memory"))
# if not USE_S3:
#     MEMORY_DIR.mkdir(exist_ok=True)

# # Initialize S3 client if needed
# if USE_S3:
#     s3_client = boto3.client("s3")


# # Load personality details from me.txt
# def load_personality() -> str:
#     me_file = Path("me.txt")
#     if me_file.exists():
#         with open(me_file, "r", encoding="utf-8") as f:
#             return f.read().strip()
#     return "You are a helpful AI assistant."


# PERSONALITY = load_personality()


# # Memory management functions
# def get_memory_path(session_id: str) -> str:
#     return f"{session_id}.json"


# def load_conversation(session_id: str) -> List[Dict]:
#     """Load conversation history from S3 or local storage"""
#     if USE_S3:
#         try:
#             response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
#             return json.loads(response["Body"].read().decode("utf-8"))
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "NoSuchKey":
#                 return []
#             raise
#     else:
#         # Local file storage
#         file_path = MEMORY_DIR / get_memory_path(session_id)
#         if file_path.exists():
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         return []


# def save_conversation(session_id: str, messages: List[Dict]):
#     """Save conversation history to S3 or local storage"""
#     if USE_S3:
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=get_memory_path(session_id),
#             Body=json.dumps(messages, indent=2, ensure_ascii=False),
#             ContentType="application/json",
#         )
#     else:
#         # Local file storage
#         file_path = MEMORY_DIR / get_memory_path(session_id)
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(messages, f, indent=2, ensure_ascii=False)


# # Request/Response models
# class ChatRequest(BaseModel):
#     message: str
#     session_id: Optional[str] = None


# class ChatResponse(BaseModel):
#     response: str
#     session_id: str


# @app.get("/")
# async def root():
#     return {
#         "message": "AI Digital Twin API with Memory",
#         "memory_enabled": True,
#         "storage": "S3" if USE_S3 else "local",
#     }


# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "use_s3": USE_S3}


# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     try:
#         # Generate session ID if not provided
#         session_id = request.session_id or str(uuid.uuid4())

#         # Load conversation history
#         conversation = load_conversation(session_id)

#         # Build system message using me.txt
#         messages = [{"role": "system", "content": PERSONALITY}]

#         # Add conversation history (keep last 10 messages for context window)
#         for msg in conversation[-10:]:
#             messages.append({"role": msg["role"], "content": msg["content"]})

#         # Add current message
#         messages.append({"role": "user", "content": request.message})

#         # Call Groq API
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=messages
#         )

#         assistant_response = response.choices[0].message.content

#         # Update conversation history with timestamps
#         conversation.append(
#             {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
#         )
#         conversation.append(
#             {
#                 "role": "assistant",
#                 "content": assistant_response,
#                 "timestamp": datetime.now().isoformat(),
#             }
#         )

#         # Save updated conversation
#         save_conversation(session_id, conversation)

#         return ChatResponse(
#             response=assistant_response,
#             session_id=session_id
#         )

#     except Exception as e:
#         print(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/conversation/{session_id}")
# async def get_conversation(session_id: str):
#     """Retrieve conversation history"""
#     try:
#         conversation = load_conversation(session_id)
#         return {"session_id": session_id, "messages": conversation}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/sessions")
# async def list_sessions():
#     """List all conversation sessions (Local storage only)"""
#     sessions = []
#     if not USE_S3:
#         for file_path in MEMORY_DIR.glob("*.json"):
#             session_id = file_path.stem
#             with open(file_path, "r", encoding="utf-8") as f:
#                 conversation = json.load(f)
#                 sessions.append({
#                     "session_id": session_id,
#                     "message_count": len(conversation),
#                     "last_message": conversation[-1]["content"] if conversation else None
#                 })
#     return {"sessions": sessions}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("DEFAULT_AWS_REGION", "us-east-1")
)

# Bedrock Model ID (Using global cross-region inference profile)
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.amazon.nova-2-lite-v1:0")

# Memory storage configuration (AWS S3 vs Local)
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = Path(os.getenv("MEMORY_DIR", "../memory"))

if not USE_S3:
    MEMORY_DIR.mkdir(exist_ok=True)

# Initialize S3 client if enabled
if USE_S3:
    s3_client = boto3.client("s3")

# Load personality from me.txt directly
def load_personality() -> str:
    me_file = Path("me.txt")
    if me_file.exists():
        with open(me_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are Sameer's Digital Twin, an AI Engineer and Cybersecurity Expert."

PERSONALITY = load_personality()

def get_memory_path(session_id: str) -> str:
    return f"{session_id}.json"

def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from S3 or local storage"""
    if USE_S3:
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] in ["NoSuchKey", "404"]:
                return []
            raise
    else:
        file_path = MEMORY_DIR / get_memory_path(session_id)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to S3 or local storage"""
    if USE_S3:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=get_memory_path(session_id),
            Body=json.dumps(messages, indent=2, ensure_ascii=False),
            ContentType="application/json",
        )
    else:
        file_path = MEMORY_DIR / get_memory_path(session_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

def call_bedrock(conversation: List[Dict], user_message: str) -> str:
    """Call AWS Bedrock using the Converse API with native system parameter"""
    
    # Pass system prompt natively via the system parameter
    system_prompts = [{"text": PERSONALITY}]
    
    # Build messages in Bedrock Converse API format
    messages = []
    
    # Append up to last 10 messages for context
    for msg in conversation[-10:]:
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })
    
    try:
        # Call Bedrock using the converse API
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=system_prompts,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        # Extract the response text
        return response["output"]["message"]["content"][0]["text"]
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ValidationException':
            print(f"Bedrock validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid message format for Bedrock")
        elif error_code == 'AccessDeniedException':
            print(f"Bedrock access denied: {e}")
            raise HTTPException(status_code=403, detail="Access denied to Bedrock model")
        else:
            print(f"Bedrock error: {e}")
            raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")

# Data models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    return {
        "message": "AI Digital Twin API (Powered by AWS Bedrock)",
        "storage": "S3" if USE_S3 else "local",
        "ai_model": BEDROCK_MODEL_ID
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "use_s3": USE_S3,
        "bedrock_model": BEDROCK_MODEL_ID
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        conversation = load_conversation(session_id)

        # Call Bedrock for response using conversation history and user message
        assistant_response = call_bedrock(conversation, request.message)

        # Update history with ISO timestamps
        conversation.append(
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
        )
        conversation.append(
            {"role": "assistant", "content": assistant_response, "timestamp": datetime.now().isoformat()}
        )

        save_conversation(session_id, conversation)

        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)