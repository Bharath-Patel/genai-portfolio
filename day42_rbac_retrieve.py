import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
collection_name = "genai_notes_rbac"


def retrieve_with_rbac(question:str, user_role:str, top_k:int = 3):
    query_embedding = model.encode(question).tolist()
    role_filter = Filter(
        must=[
            FieldCondition(
                key="role",
                match=MatchAny(any=[user_role])
            )
        ]
    )

    results = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        query_filter = role_filter,
        limit = top_k
    )
    return results.points
if __name__ == "__main__":
    print("\n=== query as 'engineer' ===")
    results = retrieve_with_rbac("What did I learn about async programming?",user_role ="engineer")
    print(f"Number of results found are {len(results)}")
    for r in results:
        print(f"source : {r.payload['source']} and score is {r.score:.3f}")
    print("\n=== Same query as 'admin' ===")
    results = retrieve_with_rbac("What did I learn about async programming?", user_role="admin")
    print(f"Results found: {len(results)}")
    for r in results:
        print(f"  Source: {r.payload['source']}, Score: {r.score:.3f}")