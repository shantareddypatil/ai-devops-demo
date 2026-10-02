import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_cohere import ChatCohere
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cohere_api_key = os.getenv("COHERE_API_KEY")
model = os.getenv("MODEL_NAME", "command-a-03-2025")
llm = ChatCohere(cohere_api_key=cohere_api_key, temperature=0.1, model=model) if cohere_api_key else None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ask")
def ask(q: str):
    if not llm:
        return {"answer": f"(demo mode) you asked: {q}"}
    response = llm.invoke(q)
    return {"answer": response.content}
@app.get("/add")
def add(a:int, b:int):
    return a+b