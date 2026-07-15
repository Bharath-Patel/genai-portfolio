from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams,Distance, PointStruct

model = SentenceTransformer("all-MiniLM-L6-v2")
sentences = [
    "I love my dog",
    "My puppy is the best",
    "The stock market crashed today",
    "I enjoy hiking in the mountains",
]

client = QdrantClient("http://localhost:6333") #connect to quadrant client running locally in docker 

#create a collection in qdrant by mentioning the name of collection, vector size and similarity math 
if not client.collection_exists("first_collection"):
    client.create_collection(collection_name = "first_collection",
                vectors_config = VectorParams(size=384,distance=Distance.COSINE)) 

#Crate embeddings for sentences list
embeddings = model.encode(sentences)

#since in qdrant everything we store(every single thing) is a point and point is bundle of point ID, vector(Actual embedding) and the payload(human readable info attached to the vector). Using PointStruct we package  point ID,vector and payload into a point object, formatted as qdrant expects.
#so when we create embeddings for sentences it returns a numpy array, but qdrant expects a python list, so we use .tolist() to convert the embeddings from numpy array to a list
points=[PointStruct(id=i,vector=embeddings[i].tolist(),payload={"text": sentences[i]})
        for i in range(len(sentences))]

#insert(upsert) points into collection
client.upsert(collection_name="first_collection",points=points)

query="Tell me about pets"
query_embedding = model.encode(query).tolist()

results = client.query_points(
    collection_name="first_collection",
    query=query_embedding,
    limit=2 # top 2 closest matches
)

print(f"\n Query: {query}")
print("Top matches:")
for r in results.points: # results is a wrapper object; .points holds the actual match list
    print(f" Score : {r.score:.3f} --  Text : {r.payload['text']}")
