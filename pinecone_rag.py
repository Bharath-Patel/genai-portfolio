from sentence_transformers import SentenceTransformer,CrossEncoder
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from groq import Groq
import boto3,json
from types import SimpleNamespace

load_dotenv()

bedrock = boto3.client('bedrock-runtime',
                    region_name= os.getenv("AWS_REGION"),
                    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                )

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(
    url = os.getenv("QDRANT_URL"),
    api_key = os.getenv("QDRANT_API_KEY")
)
collection_name = "genai_notes"
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# --- Pinecone (second vector store) ---
pinecone_index_name = "genai-notes"
_pinecone_cache = {}

def _get_pinecone_index():
    # Created on first use, not at import time. That way running with
    # vector_store="qdrant" never needs the pinecone package, an API key, or
    # a network call, so existing deployments keep working untouched.
    if "index" not in _pinecone_cache:
        from pinecone import Pinecone
        pc = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))
        _pinecone_cache["index"] = pc.Index(pinecone_index_name)
    return _pinecone_cache["index"]

def retrieve(question: str, wide_k: int = 10, final_k: int=3, vector_store: str = "qdrant"):
    query_embedding = model.encode(question).tolist()

    if vector_store == "qdrant":
        results = client.query_points(
            collection_name = collection_name,
            query = query_embedding,
            limit = wide_k
        )
        candidates = results.points
    elif vector_store == "pinecone":
        results = _get_pinecone_index().query(
            vector = query_embedding,
            top_k = wide_k,
            include_metadata = True      # without this, Pinecone returns scores but no text
        )
        # Pinecone calls it .metadata, Qdrant calls it .payload. Wrap each match so it has
        # .id, .score and .payload like a Qdrant point; build_prompt() and every caller
        # downstream then work without any change.
        candidates = [
            SimpleNamespace(id = m.id, score = m.score, payload = m.metadata)
            for m in results.matches
        ]
    else:
        raise ValueError("vector_store must be 'qdrant' or 'pinecone'")

    if not candidates:
        return [], 0.0     # was `return []`, which crashed the caller's two-value unpack
    # Keep the vector store's original top score - THIS is what the guardrail will check
    top_score = candidates[0].score
    pairs = [(question,c.payload['text']) for c in candidates]
    rerank_scores = reranker.predict(pairs)

    scored = list(zip(candidates,rerank_scores))
    scored.sort(key=lambda x:x[1],reverse=True)
  
    top_candidates = [ c for c, scores in scored[:final_k]]
    return top_candidates,top_score

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

def answer_question(question:str,provider: str = "groq", similarity_thrshold: float=0.3, vector_store: str = "qdrant"):
    retrieved_chunks, top_score=retrieve(question, vector_store = vector_store)
    retrieved_chunks.sort(key=lambda x:x.score, reverse=True)
 
    if not retrieved_chunks:
        return "I don't have information about that in my documents.", []   

    if top_score < similarity_thrshold:
        return ("I don't have information about that in my documents.",retrieved_chunks)
    prompt = build_prompt(question,retrieved_chunks)

    if provider == "bedrock":
        context_text = "\n\n".join(r.payload["text"] for r in retrieved_chunks) #Bedrock's grounding check specifically requires the context and the query to arrive as two separate, individually-tagged pieces — not merged into one block of text
        answer = generate_with_bedrock(question,context_text)
    else:
        answer = generate_with_groq(prompt)
    #print("top 3 retrievals with respective similarity scores")
    # for r in retrieved_chunks:
    #     print(f"- {r.payload['source']} (score {r.score:.3f})")
    return answer,retrieved_chunks   

def generate_with_bedrock(question: str, context: str) -> str:
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "guardContent": {
                            "text": {
                                "text": context,
                                "qualifiers": ["grounding_source"]
                            }
                        }
                    },
                    {
                        "guardContent": {
                            "text": {
                                "text": question,
                                "qualifiers": ["query"] #qualifiers is mentioned,only grounding check reads it → word/content/PII filters skip it entirely.
                            }
                        }
                    },
                    {"guardContent": {"text": {"text": question}}} #no qualifiers key at all → word/content/PII filters now see it.
                ]
            }
        ],
        system=[{"text": (
                "You are a RAG assistant. Answer using ONLY the exact information in the "
                "provided context — do not add explanations, steps, or details from your "
                "own general knowledge, even if you know them. If the context doesn't "
                "fully answer the question, say only what the context actually states."
            )}],
        inferenceConfig={"temperature": 0},
        guardrailConfig={
            "guardrailIdentifier": os.getenv("BEDROCK_GUARDRAIL_ID"),
            "guardrailVersion": os.getenv("BEDROCK_GUARDRAIL_VERSION", "DRAFT"),
            "trace": "enabled"
        }
    )
    #print(json.dumps(response.get("trace", {}), indent=2, default=str))
    if response.get("stopReason") == "guardrail_intervened":
        #print(json.dumps(response.get("trace", {}), indent=2, default=str))
        return "This request was blocked by a content safety guardrail."

    return response["output"]["message"]["content"][0]["text"]

def generate_with_groq(prompt: str) -> str:
    response = groq.chat.completions.create(
    model = "openai/gpt-oss-20b",
    temperature=0,
    messages = [
        {"role" : "system","content" : "you are a helpful assistant answering questions based strictly on provided context."},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content

if __name__ == "__main__":
    question = "How do I control who can access my S3 bucket?"
    print("=== Groq ===")
    answer,sources = answer_question(question, provider="groq")
    print("=== Answer ===")
    print(answer)
    print("=== Bedrock ===")
    answer,sources = answer_question(question, provider="bedrock")
    print("=== Answer ===")
    print(answer)

    # Retrieval only (no LLM calls): same question against both vector stores
    print("=== Retrieval comparison: same question, both stores ===")
    for store in ("qdrant", "pinecone"):
        chunks, top = retrieve(question, vector_store = store)
        print(f"-- {store} (top vector score {top:.3f})")
        for c in chunks:
            print(f"   {c.score:.3f}  {c.payload['source']}  |  {c.payload['text'][:60]}")