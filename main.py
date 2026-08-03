from chat import chat_with_contract
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from extract import extract_text
from analyze import analyze_contract
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text(contents, file.filename)
    analysis = analyze_contract(text)

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"text": text, "history": []}

    return {"session_id": session_id, "analysis": analysis}

@app.get("/")
async def root():
    return {"status": "ClauseCompass backend is running"}
@app.post("/chat")
async def chat(session_id: str, message: str):
    if session_id not in sessions:
        return {"error": "Invalid session_id"}
    session = sessions[session_id]
    response = chat_with_contract(session["text"], session["history"], message)
    session["history"].append({"role": "user", "content": message})
    session["history"].append({"role": "assistant", "content": response})
    return {"response": response}

@app.post("/chat/{session_id}")
async def chat(session_id: str, message: dict):
    if session_id not in sessions:
        return {"error": "Session not found. Please upload a contract first."}

    session = sessions[session_id]
    reply = chat_with_contract(session["text"], session["history"], message["text"])

    session["history"].append({"role": "user", "content": message["text"]})
    session["history"].append({"role": "assistant", "content": reply})

    return {"reply": reply}    