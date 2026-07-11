from fastapi import FastAPI
import os
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def gather_stream(question:str, temperature:float, system_prompt:str):
    stream = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        messages=[{"role":"system","content":system_prompt},
                   {"role":"user","content":question}],
        stream=True #this is the key change: ask Groq to stream chunks
    )
    # Loop through each chunk as it arrives from Groq
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content: # some chunks are empty (e.g. the very first/last one)
            yield content # is what makes your Python function produce data piece by piece internally

@app.get("/chat-stream")
def chat_stream(
    question: str = "what is the capital of Japan?",
    temperature: float = 0.7,
    system_prompt:str = "You are conscinece assistant"):

    return StreamingResponse( 
        gather_stream(question,temperature,system_prompt),
        media_type="text/plain"
    )

    #streaming response sends the data chunk by chunk as it's produced(this is what actually makes it "stream")
    #streaming response is what takes those yielded pieces and actually forwards them over the network connection as they arrive,

    #curl -N "localhost:8000/chat-stream?question=Write%20a%20short%20paragraph%20about%20the%20ocean"
    #media_type tells the reciever what format to expect or how to interpret the bytes once they arrive