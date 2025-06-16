from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoTokenizer
from llama_cpp import Llama
import os

# --- Load model ---
model_path = "model/unsloth.Q4_K_M.gguf"  # Change to your GGUF file
llm = Llama(    
    model_path="model/unsloth.Q4_K_M.gguf",
    n_gpu_layers=-1,         # 🚀 Full model on GPU
    n_ctx=1024,              # Reasonable context
    n_threads=8,             # Match your CPU cores
    use_mlock=True,          # Lock into memory
    f16_kv=True ,)

# --- Load tokenizer if needed (for tokenizer-based templating) ---
# tokenizer = AutoTokenizer.from_pretrained("path/to/tokenizer")

# --- FastAPI setup ---
app = FastAPI()

# Serve static files (e.g., index.html, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("static/index.html")

# --- Request/Response models ---
class PromptRequest(BaseModel):
    instruction: str
    input: str

@app.post("/generate")
async def generate_text(prompt: PromptRequest):
    alpaca_prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{prompt.instruction}

### Input:
{prompt.input}

### Response:
"""
    output = llm(alpaca_prompt, max_tokens=128, temperature=0.7,top_p=0.95,)
    return {"response": output["choices"][0]["text"].strip()}
