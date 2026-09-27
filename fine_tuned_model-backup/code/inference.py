from sentence_transformers import SentenceTransformer

def model_fn(model_dir): #runs once, when the container starts — loads your model into memory.
    return SentenceTransformer(model_dir)

def predict_fn(input_data, model): #runs on every request — takes the JSON you send,
    text = input_data["inputs"] #pulls out "inputs",
    embedding = model.encode(text) # encodes it
    return embedding.tolist() #and returns a plain list (JSON-serializable) instead of a raw tensor