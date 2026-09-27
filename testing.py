from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
local_embedding = model.encode("How do I control who can access my S3 bucket?")
print(local_embedding[:10])  # first 10 numbers, for a quick visual comparison