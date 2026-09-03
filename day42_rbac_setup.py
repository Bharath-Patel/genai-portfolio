import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance,PointStruct,PayloadSchemaType

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url = os.getenv("QDRANT_URL"),api_key =os.getenv("QDRANT_API_KEY"))
splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

collection_name = "genai_notes_rbac"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name = collection_name,
        vectors_config = VectorParams(size=384, distance=Distance.COSINE)
    )

    client.create_payload_index(
        collection_name=collection_name,
        field_name = "role",
        field_schema = PayloadSchemaType.KEYWORD #telling Qdrant what kind of data type this field holds, and therefore what kind of matching makes sense for it
    )    #KEYWORD means: "this field holds exact, discrete string values — like categories or tags
    
FILE_ROLE_MAP = {
    "aws_s3.txt": ["engineer", "admin"],
    "aws_lambda.txt": ["engineer", "admin"],
    "terraform_state.txt": ["engineer", "admin"],
    "my_personal_notes.txt": ["admin"]
}

data_folder = "data"
point_id = 0
all_points=[]

for filename in os.listdir(data_folder):
    if not filename.endswith(".txt"):
        continue
        
    allowed_roles = FILE_ROLE_MAP.get(filename,["engineer"])
    filepath = os.path.join(data_folder,filename)
    with open(filepath,"r") as f:
        text = f.read()

    chunks = splitter.split_text(text)
    embeddings = model.encode(chunks)

    for i,chunk in enumerate(chunks):
        all_points.append(
            PointStruct(
                id = point_id,
                vector = embeddings[i].tolist(),
                payload = {"text" : chunk,"source":filename,"role": allowed_roles}
            )
        )
        point_id += 1
client.upsert(collection_name = collection_name, points = all_points)
print(f"Inserted {len(all_points)} points to '{collection_name}' with role tagging")
