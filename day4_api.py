from fastapi import FastAPI
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/chat")
def chat(
    question: str = "what is the capital of India",
    temperature: float = 0.7,
    system_prompt: str = "You are a helpful, concise assistant."):

    groq_response = groq_client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        temperature = temperature,
        messages = [
            {"role" : "system", "content": system_prompt},
            {"role" : "user", "content": question}
        ]
    )

    return {
        "answer" : groq_response.choices[0].message.content,
        "temperature_used" : temperature,
        "system_prompt_used" : system_prompt
    }