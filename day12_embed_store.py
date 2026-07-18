import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams,Distance, PointStruct

model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
)

client = QdrantClient("http://localhost:6333")
collection_name = "genai_notes"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name = collection_name,
        vectors_config = VectorParams(size = 384, distance = Distance.COSINE)
    )

data_folder = "data"
all_points = []
point_id = 0


for filename in os.listdir(data_folder):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(data_folder,filename)

    with open(filepath,"r") as f:
        text = f.read()

    chunks=splitter.split_text(text)

    embeddings = model.encode(chunks)

    for i,chunk in enumerate(chunks):
        all_points.append(
            PointStruct(
                id = point_id,
                vector = embeddings[i].tolist(),
                payload = {"text": chunk, "source": filename}
        ))
        point_id += 1


client.upsert(collection_name=collection_name,points=all_points)
print(f"\nTotal chunks embedded and stored: {len(all_points)}")

query = "How do I manage state file locking in Terraform?"
query_embedding = model.encode(query).tolist()

results = client.query_points(
    collection_name=collection_name,
    query=query_embedding,
    limit=3 # top 3 closest matches
)

print(f"\nQuery: '{query}'")
print("Top matches:")
for r in results.points:
    print(f"  Score: {r.score:.3f} — Source: {r.payload['source']}")
    print(f"  Text: {r.payload['text'][:150]}...")
    print()