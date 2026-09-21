import json
import os
import boto3
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

collection_name = "genai_notes_sagemaker"


def get_sagemaker_embedding(text: str):
    response = runtime.invoke_endpoint(
        EndpointName="genai-embedding-endpoint",
        ContentType="application/json",
        Body=json.dumps({"inputs": text}),
    )
    result = json.loads(response["Body"].read())
    return result[0]  # unwrap the outer list - same shape you saw earlier


if not qdrant.collection_exists(collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
data_folder = "data"
all_points = []
point_id = 0

for filename in os.listdir(data_folder):
    if not filename.endswith(".txt"):
        continue
    with open(os.path.join(data_folder, filename), "r") as f:
        text = f.read()
    chunks = splitter.split_text(text)
    for chunk in chunks:
        embedding = get_sagemaker_embedding(chunk)
        all_points.append(
            PointStruct(id=point_id, vector=embedding, payload={"text": chunk, "source": filename})
        )
        point_id += 1
        print(f"Embedded chunk {point_id} via SageMaker endpoint")

qdrant.upsert(collection_name=collection_name, points=all_points)
print(f"\nInserted {len(all_points)} points into '{collection_name}' using SageMaker-hosted embeddings")

# Quick retrieval test
query = "How do I control who can access my S3 bucket?"
query_vector = get_sagemaker_embedding(query)
results = qdrant.query_points(collection_name=collection_name, query=query_vector, limit=3)
print(f"\nQuery: {query}")
for r in results.points:
    print(f"Score: {r.score:.3f} — {r.payload['text'][:80]}...")