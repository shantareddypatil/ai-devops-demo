import os
from fastapi import FastAPI
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()
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
