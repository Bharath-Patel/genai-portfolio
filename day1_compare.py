#compare responses from a cloud model and a local model(LLM's).
#Groq – A cloud-based AI inference service (requires an API key and internet).
#Ollama – A locally running LLM on your own computer (does not require internet after the model is downloaded).

from dotenv import load_dotenv #to read variables stored inside a .env file.
import os #the OS module let's pyhton interact with operating system
from groq import Groq #imports the official Groq Python client.
import ollama #imports the Ollama Python package. Communicates with the Ollama service running on your own machine.

load_dotenv() #loads the env variable in our .env file and stores the var in memory

question = "what is the capital of India?"

groq_client=Groq(api_key=os.getenv("GROQ_API_KEY")) #creates a groq client object to authenticate with groq API key loaded from env file

groq_response=groq_client.chat.completions.create(   #Send Request to Groq by calling the chat completion API i.e asking to Generate an answer for this conversation.
                model = "llama-3.1-8b-instant", #tells grow which LLM to use
                messages = [ 
                    { "role": "user",
                      "content": question}
                ] #chat models expect a list of messages.
)
print(type(groq_response))
print("###groq response #####")
print(groq_response.choices[0].message.content)

Ollama_response = ollama.chat(  #send request to llama runnning in the local
                model = "llama3.2",
                messages = [ 
                    { "role": "user",
                      "content": question}
                ]

)

print("\n###ollama response####")
print(type(Ollama_response))
print(Ollama_response.message.content)

#data = Ollama_response.model_dump() #to get the response , so that we can pick the message
#print(data)