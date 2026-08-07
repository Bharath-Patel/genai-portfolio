from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url="http://localhost:6333")
collection_name = "genai_notes"

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

question = "Why would my Lambda function time out?"

query_embedding = model.encode(question).tolist()


def retrieve_wide(question:str, top_k: int=10):    
    results = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        limit = top_k
    )
    return results.points

def rerank(question:str , candidates, top_n: int=3):
    """Stage 2: NEW - cross-encoder re-scores each candidate against the question directly."""
    # Build (question, chunk_text) pairs - this is the "look at both together" part
    pairs = [ (question,c.payload['text']) for c in candidates]
    rerank_scores = reranker.predict(pairs)

    scored=list(zip(candidates,rerank_scores))

    scored.sort(key=lambda x:x[1],reverse=True)

    return scored[:top_n]

wide_candidates = retrieve_wide(question, top_k=10)

print("=== Stage 1: Qdrant's original vector similarity scores ===")
for c in wide_candidates:
    print(f" {c.score:.3f} - {c.payload['text'][:80]}...")

reranked = rerank(question,wide_candidates,top_n=3)

print("\n=== Stage 2: Cross-encoder rerank scores ===")

for candidate,rerank_score in reranked:
    print(f" {rerank_score:.3f} - {candidate.payload['text'][:80]}...")
