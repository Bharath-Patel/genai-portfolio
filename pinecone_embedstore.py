import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
)

pc = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

# Pinecone index names: 1-45 characters, lowercase letters, digits and hyphens only.
# (Qdrant's "genai_notes" has an underscore, which Pinecone would reject.)
index_name = "genai-notes"

if not pc.has_index(index_name):
    pc.create_index(
        name = index_name,
        dimension = 384,          # same as all-MiniLM-L6-v2 and the Qdrant collection
        metric = "cosine",        # same as Distance.COSINE
        spec = ServerlessSpec(cloud = "aws", region = "us-east-1")  # the free plan only allows this region
    )
    # create_index waits until the index is ready before returning

index = pc.Index(index_name)

stats = index.describe_index_stats()
# NOTE: these counts can lag a recent write, so this guard is reliable on a re-run later,
# but not in the first few seconds after an upsert.
if stats.total_vector_count > 0:
    print(f"Index already has {stats.total_vector_count} vectors — skipping re-embedding.")
else:

    data_folder = "data"  # data folder in my local
    all_records = []
    record_id = 0

    for filename in os.listdir(data_folder):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(data_folder, filename)

        with open(filepath, "r") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        embeddings = model.encode(chunks)

        for i, chunk in enumerate(chunks):
            all_records.append({
                "id": str(record_id),                  # Pinecone ids must be strings (Qdrant allowed ints)
                "values": embeddings[i].tolist(),      # Qdrant called this "vector"
                "metadata": {"text": chunk, "source": filename}   # Qdrant called this "payload"
            })
            record_id += 1

    # One upsert after all files are read (the Qdrant version re-upserted the growing
    # list after every file). batch_size splits it into requests of 100 records.
    index.upsert(vectors = all_records, batch_size = 100)
    print(f"\nTotal chunks embedded and stored: {len(all_records)}")

    # Pinecone is eventually consistent: just-upserted records can take a few seconds to
    # become searchable. Wait until the index reports them all (up to ~60 seconds).
    for _ in range(30):
        if index.describe_index_stats().total_vector_count >= len(all_records):
            break
        time.sleep(2)
    else:
        print("Warning: records not all visible yet; the query below may miss some.")

query = "How do I manage state file locking in Terraform?"
query_embedding = model.encode(query).tolist()

results = index.query(
    vector = query_embedding,
    top_k = 3,                  # top 3 closest matches (Qdrant called this "limit")
    include_metadata = True     # Qdrant returned the payload by default; Pinecone needs this flag
)

print(f"\nQuery: '{query}'")
print("Top matches:")
for r in results.matches:       # Qdrant: results.points
    print(f"  Score: {r.score:.3f} — Source: {r.metadata['source']}")
    print(f"  Text: {r.metadata['text'][:150]}...")
    print()