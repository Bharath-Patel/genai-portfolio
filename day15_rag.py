from sentence_transformers import SentenceTransformer,CrossEncoder
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(
    url = os.getenv("QDRANT_URL"),
    api_key = os.getenv("QDRANT_API_KEY")
)
collection_name = "genai_notes"
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def retrieve(question: str, wide_k: int = 10, final_k: int=3):
    query_embedding = model.encode(question).tolist()
    results = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        limit = wide_k
    )
    candidates = results.points

    if not candidates:
        return []
    # Keep Qdrant's original top score - THIS is what the guardrail will check
    qdrant_top_score = candidates[0].score
    pairs = [(question,c.payload['text']) for c in candidates]
    rerank_scores = reranker.predict(pairs)

    scored = list(zip(candidates,rerank_scores))
    scored.sort(key=lambda x:x[1],reverse=True)
  
    top_candidates = [ c for c, scores in scored[:final_k]]

    return top_candidates,qdrant_top_score

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

def answer_question(question:str, similarity_thrshold: float=0.3):
    retrieved_chunks, qdrant_top_score=retrieve(question)
    if not retrieved_chunks:
        return "I don't have information about that in my documents.", []   

    if qdrant_top_score < similarity_thrshold:
        return ("I don't have information about that in my documents.",retrieved_chunks)
    prompt = build_prompt(question,retrieved_chunks)
    response = groq.chat.completions.create(
    model = "llama-3.1-8b-instant",
    temperature=0,
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

    
    