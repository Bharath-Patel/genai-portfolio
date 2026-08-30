import asyncio
import time
from dotenv import load_dotenv
import os
from groq import AsyncGroq
import ollama

load_dotenv()

question = "which is the capital of India"

async def callgroq():
    await asyncio.sleep(2)
    groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    groq_response = await groq_client.chat.completions.create(
                model = "openai/gpt-oss-20b",
                messages = [ 
                    { "role": "user",
                      "content": question}
                ]
    )

    return "Groq: " + groq_response.choices[0].message.content

async def call_ollama():
    await asyncio.sleep(2)
    ollama_client = ollama.AsyncClient()
    Ollama_response = await ollama_client.chat(
                    model="llama3.2",
                    messages=[{"role": "user", "content": question}]
    )
    return "Ollama: " + Ollama_response.message.content

async def call_ollama_again():
    await asyncio.sleep(2)
    ollama_client = ollama.AsyncClient()
    Ollama_response = await ollama_client.chat(
                    model="llama3.2",
                    messages=[{"role": "user", "content": "what is the capital of Japan"}]        
    )

    return "Ollama: " + Ollama_response.message.content

async def main():
    start = time.time()
    results = await asyncio.gather(callgroq(),call_ollama(),call_ollama_again()) #Fire them all concurrently, and pause right here(used await) until the very last one finishes and hands back its data.
    #result_groq = await callgroq()
    # result_ollama = await call_ollama()
    # result_ollama_again = await call_ollama_again()
    # results = (result_groq,result_ollama,result_ollama_again)
    end = time.time()
    for r in results:
        print(r)
        print("=====")
    print(f"Total time (concurrent): {end - start:.2f} seconds")

asyncio.run(main()) #Normal Python doesn't know how to talk to an async function directly. asyncio.run(main()) acts as the starter motor that boots up the Event Loop and hands control over to your async code.
#Async code requires a manager called an Event Loop to coordinate the pausing, switching, and resuming of functions.