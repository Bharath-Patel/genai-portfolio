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

#to test after starting he fastapi in one terminal by runnin uvicorn day3_api:app --reload
#in the next terminal run curl "localhost:8000/chat?question=What%20is%20the%20capital%20of%20India%3F"
#instead of %20 and %3F use , curl -G "localhost:8000/chat-stream" --data-urlencode "question=what is the capital of India", this is for GET request, for POST requests we will see next.