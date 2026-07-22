from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient("http://localhost:6333")
collection_name = "genai_notes"
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


def retrieve(question: str, topK: int = 3):
    query_embedding = model.encode(question).tolist()
    results = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        limit = topK
    )
    return results.points

def build_prompt(question:str, retrieved_chunks) -> str:
    context = "\n\n".join(f"[Source: {r.payload['source']}]\n{r.payload['text']}"
    for r in retrieved_chunks)
    prompt = f"""Answer the question using ONLY the context below.
    if the answer is not in the context, say "I don't have information about that in my documents."

Context:
{context}
Question: {question}
"""
    return prompt

def answer_question(question:str):
    retrieved_chunks=retrieve(question)
    prompt = build_prompt(question,retrieved_chunks)
    response = groq.chat.completions.create(
    model = "llama-3.1-8b-instant",
    messages = [
        {"role" : "system","content" : "you are a helpful assistant answering questions based strictly on provided context."},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content, retrieved_chunks

if __name__ == "__main__":
    question = "How do I control who can access my S3 bucket?"
    answer, sources = answer_question(question)
    print(f"Question: {question}\n")
    print(f"Answer: {answer}\n")
    for r in sources:
        print(f"- {r.payload['source']} (score {r.score:.3f})")

    
    