from fastapi import FastAPI
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

app = FastAPI() #creating a FastAPI application object.

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/chat") #@app is the decorator,if any HTTP GET request to /chat, run the function immediately below
def chat(question: str="What is the capital of India?"):
    groq_response = groq_client.chat.completions.create(
                    model = "llama-3.1-8b-instant",
                    messages = [ 
                    { "role": "user",
                      "content": question}
                ]
    )

    return {"answer" : groq_response.choices[0].message.content}
