# from sentence_transformers import SentenceTransformer
# from sentence_transformers.util import cos_sim

# question = "What does Amazon S3 Storage Lens provide for analyzing and optimizing storage usage across an organization?"
# context = "Amazon S3 Storage Lens \u2013 Understand, analyze, and optimize your storage. S3 Storage Lens provides 60+ usage and activity metrics and interactive dashboards to aggregate data for your entire organization, specific accounts, AWS Regions, buckets, or prefixes.\n\nStorage Class Analysis \u2013 Analyze storage access patterns to decide when it's time to move data to a more cost-effective storage class."

# original_model = SentenceTransformer("all-MiniLM-L6-v2")
# finetuned_model = SentenceTransformer("fine_tuned_model")

# q_emb_original = original_model.encode(question)
# c_emb_original = original_model.encode(context)
# original_score = cos_sim(q_emb_original, c_emb_original)

# q_emb_finetuned = finetuned_model.encode(question)
# c_emb_finetuned = finetuned_model.encode(context)
# finetuned_score = cos_sim(q_emb_finetuned, c_emb_finetuned)

# print("Original model similarity:", original_score.item())
# print("Fine-tuned model similarity:", finetuned_score.item())

import json
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

original_model = SentenceTransformer("all-MiniLM-L6-v2")
finetuned_model = SentenceTransformer("fine_tuned_model") #local folder of model artifact
#finetuned_model = SentenceTransformer("/Users/htk/sagemaker_fine_tuned_model") #model artifact downloaded from s3 after sagemaker training

pairs = []
with open("training_pairs_file.jsonl") as f:
    for line in f:
        pairs.append(json.loads(line))

original_total = 0
finetuned_total = 0

for p in pairs:
    q = p["question"]
    c = p["context"]
    original_total += cos_sim(original_model.encode(q), original_model.encode(c)).item()
    finetuned_total += cos_sim(finetuned_model.encode(q), finetuned_model.encode(c)).item()

print("Average original similarity:", original_total / len(pairs))
print("Average finetuned similarity:", finetuned_total / len(pairs))