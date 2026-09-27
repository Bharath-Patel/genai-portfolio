import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

pairs=[]
with open("training_pairs_file.jsonl") as f:
    for line in f:
        pairs.append(json.loads(line))

train_examples = [InputExample(texts=[p["question"],p["context"]]) for p in pairs]

model = SentenceTransformer("all-MiniLM-L6-v2")
train_dataloader = DataLoader(train_examples,shuffle=True,batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives = [(train_dataloader,train_loss)],
    epochs =3,
    warmup_steps=10,
    output_path="fine_tuned_model"
)

print("Done — saved to fine_tuned_model/")