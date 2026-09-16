import os
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
collection_name = "genai_notes"

# --- One-time setup: build the BM25 index over ALL chunks ---
# BM25 needs the full corpus upfront, unlike Qdrant's per-query search
print("Building BM25 index...")
all_points = client.scroll(collection_name=collection_name, limit=1000)[0]
corpus_texts = [p.payload['text'] for p in all_points]
corpus_ids = [p.id for p in all_points]
tokenized_corpus = [text.lower().split() for text in corpus_texts]
bm25 = BM25Okapi(tokenized_corpus)
print(f"BM25 index built over {len(corpus_texts)} chunks")

def semantic_search(question: str, top_k: int = 10):
    query_embedding = model.encode(question).tolist()
    results = client.query_points(collection_name = collection_name,query=query_embedding,limit=top_k)
    return [(p.id,p.payload['text'],p.payload['source']) for p in results.points]

def bm25_search(question:str, top_k: int = 10):
    tokenize_query = question.lower().split()
    scores = bm25.get_scores(tokenize_query)
    ranked_indices = sorted(range(len(scores)), key=lambda i:scores[i], reverse=True)[:top_k]
    return [(corpus_ids[i], corpus_texts[i]) for i in ranked_indices]

def hybrid_retrieve(question:str,top_k: int = 10,k: int = 60):
    semantic_results = semantic_search(question, top_k)
    bm25_results=bm25_search(question,top_k)
    rrf_scores = {}
    id_to_text = {}

    for rank,(chunk_id,text,source) in enumerate(semantic_results):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id,0) + 1 / (k + rank)
        id_to_text[chunk_id] = (text,source)

    for rank, (chunk_id, text) in enumerate(bm25_results):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank)
    
    ranked = sorted(rrf_scores.items(), key=lambda x:x[1], reverse=True)[:top_k]
    return [(chunk_id,id_to_text.get(chunk_id, ("(unknown)", "(unknown)"))[0],rrf_scores[chunk_id]) for chunk_id, _ in ranked]

if __name__ == "__main__":
    question = "How do I control who can access my S3 bucket?"
    results = hybrid_retrieve(question)
    print(f"\nQuery: {question}")
    for chunk_id, text, score in results:
        print(f"RRF score: {score:.4f} — {text[:80]}...")