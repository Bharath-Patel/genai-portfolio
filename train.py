import json
import os
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

data_dir = os.environ.get("SM_CHANNEL_TRAINING", ".")
data_file = os.path.join(data_dir, "training_pairs_file.jsonl")

pairs = []
with open(data_file) as f:
    for line in f:
        pairs.append(json.loads(line))

train_examples = [InputExample(texts=[p["question"], p["context"]]) for p in pairs]

model = SentenceTransformer("all-MiniLM-L6-v2")
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=10,
    output_path=os.environ.get("SM_MODEL_DIR", "fine_tuned_model")
)

code_dir = os.path.join(os.environ.get("SM_MODEL_DIR", "fine_tuned_model"), "code")
os.makedirs(code_dir, exist_ok=True)

inference_script = '''from sentence_transformers import SentenceTransformer

def model_fn(model_dir):
    return SentenceTransformer(model_dir)

def predict_fn(input_data, model):
    text = input_data["inputs"]
    embedding = model.encode(text)
    return embedding.tolist()
'''

with open(os.path.join(code_dir, "inference.py"), "w") as f:
    f.write(inference_script)

with open(os.path.join(code_dir, "requirements.txt"), "w") as f:
    f.write("sentence-transformers>=6.1.0\naccelerate>=1.1.0\ndatasets\n")

print("Done — saved to fine_tuned_model/, including code/ for inference.")