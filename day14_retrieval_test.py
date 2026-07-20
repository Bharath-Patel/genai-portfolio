from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient("http://localhost:6333")


collection_name = "genai_notes"

test_questions = [
    "How do I control who can access my S3 bucket?",
    "What triggers a Lambda function to run?",
    "How does Terraform know what infrastructure already exists?",
    "What did I learn about async programming?",
    "How do I store data in the cloud?"
]

for query in test_questions:
    query_embedding = model.encode(query).tolist()
    results = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        limit=2

 )

    print(f"{query}\n")
    for r in results.points:
        print(f"score is {r.score:.3f} - source document is {r.payload['source']}")
        print(f"text is {r.payload['text'][:120]}...")
    print(f"-" * 80)