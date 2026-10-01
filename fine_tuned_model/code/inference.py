from sentence_transformers import SentenceTransformer

def model_fn(model_dir):
    return SentenceTransformer(model_dir)

def predict_fn(input_data, model):
    text = input_data["inputs"]
    embedding = model.encode(text)
    return embedding.tolist()
