from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_cpp import Llama
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware
from database import SessionLocal, init_db
from models import User, ChatHistory
import uuid

# --- Initialize DB ---
init_db()

# --- Load model ---
llm = Llama(
    model_path="E:/Documents/Kuliah/Semester 6/PsykitTest/model/unsloth.Q4_K_M.gguf",
    n_gpu_layers=20,
    n_ctx=512,
    n_threads=8,
    use_mlock=True,
    f16_kv=True,
)

# --- App Setup ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret123")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email, password=password).first()
    db.close()

    if user:
        session_id = str(uuid.uuid4())
        request.session["user"] = user.email
        request.session["user_id"] = user.id
        request.session["session_id"] = session_id
        return RedirectResponse(url="/chat", status_code=302)
    return HTMLResponse("Invalid credentials", status_code=401)

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return HTMLResponse("Email already registered. <a href='/signup'>Try again</a>", status_code=400)

    # Create new user
    new_user = User(email=email, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/", status_code=302)  

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    if "user_id" not in request.session:
        return RedirectResponse("/", status_code=302)

    db = SessionLocal()
    history = db.query(ChatHistory).filter_by(user_id=request.session["user_id"]).order_by(ChatHistory.timestamp.asc()).all()
    db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "history": history
    })

@app.post("/clear_history")
async def clear_history(request: Request):
    if "user_id" not in request.session:
        return {"status": "unauthorized"}

    db = SessionLocal()
    db.query(ChatHistory).filter_by(user_id=request.session["user_id"]).delete()
    db.commit()
    db.close()
    
    return {"status": "ok"}


class PromptRequest(BaseModel):
    input: str

@app.post("/send")
async def chat(request: Request, prompt: PromptRequest):
    if "user_id" not in request.session:
        return {"error": "Not logged in"}

    instruction = "You are a psychology bot who answers user questions in a polite, empathetic, and professional manner. Your answers should be long, supportive, and thoughtful."

    alpaca_prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{prompt.input}

### Response:
"""
    output = llm(alpaca_prompt, max_tokens=128, temperature=0.7, top_p=0.95)
    reply = output["choices"][0]["text"].strip()

    db = SessionLocal()
    history = ChatHistory(user_id=request.session["user_id"], message=prompt.input, response=reply)
    db.add(history)
    db.commit()
    db.close()

    return {"response": reply}

@app.get("/history")
async def get_history(request: Request):
    if "user_id" not in request.session:
        return RedirectResponse("/", status_code=302)

    db = SessionLocal()
    records = db.query(ChatHistory).filter_by(user_id=request.session["user_id"]).order_by(ChatHistory.timestamp.desc()).all()
    db.close()

    return {"history": [{"user": h.message, "bot": h.response, "time": h.timestamp} for h in records]}
