from sentence_transformers import SentenceTransformer # let's us use a embedding model 
from sentence_transformers.util import cos_sim #cosine similarity , to compare the similarity between list of numbers as in how close they are. A similarity score of 1 means identical, 0 means unrelated and -1 means opposite

model = SentenceTransformer("all-MiniLM-L6-v2") #hugging face embedding model.It converts sentences, paragraphs, or words into dense mathematical vectors.
sentences = [
    "I love my dog",
    "My puppy is the best",
    "The stock market crashed today",
    "I enjoy hiking in the mountains",
]

embeddings = model.encode(sentences) #create embeddings(list of numbers) of sentences

print("Embedding for 'I love my dog' (first 10 numbers of many):")
print(embeddings[0][:10])
print(f"total length of this embedding: {len(embeddings[0])} numbers")

# Now compare similarity between every pair of sentences
print("=== Similarity scores (1.0 = identical meaning, 0 = unrelated) ===\n")

#comparing the similarity btw each pair of sentences

for i in range(len(embeddings)):
    for j in range(i+1,len(embeddings)):
        score = cos_sim(embeddings[i],embeddings[j]).item() #cos_sim returns a tensor, but we need a plain similarity score. .item() extracts the plain Python number out of that tensor wrapper
        print(f"'{sentences[i]}' <----> '{sentences[j]}'")
        print(f"Similarity {score:.3f}\n")