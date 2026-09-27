import os,json
from groq import Groq
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
client = QdrantClient(api_key=os.getenv("QDRANT_API_KEY"),url=os.getenv("QDRANT_URL"))

all_points=client.scroll(collection_name="genai_notes",limit=200)[0]

pairs=[]
coun = 0

for point in all_points:
    text=point.payload['text']
    response = groq.chat.completions.create(
        model = "openai/gpt-oss-20b",
        temperature = 0.7,
        messages =[
            {"role" : "system", "content" : "Generate ONE natural question that the following text would directly answer. Return only the question, nothing else"},
            {"role" : "user","content" : text}
        ]
    )
    coun += 1
    print(f"generated for text {coun}  ")
    question = response.choices[0].message.content.strip()
    pairs.append({"question" : question, "context" : text})

pairs = [p for p in pairs if p["question"].strip() != p["context"].strip() and len(p["context"]) > 50 and p["context"].strip()[0].isupper()]
# JSON Lines (.jsonl): one JSON object per line, no enclosing [ ], no commas between records.
# Not a single valid JSON document — don't read with json.load().
# Read it line by line instead: [json.loads(line) for line in f]
with open("training_pairs_file.jsonl","w") as f:
    for p in pairs:
        f.write(json.dumps(p) + "\n")
print(f"Generated {len(pairs)} training pairs")