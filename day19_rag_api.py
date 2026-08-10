from fastapi import FastAPI
from day15_rag import answer_question


app = FastAPI()

@app.get("/ask")

def ask(question: str, similarity_threshold: float = 0.3):
    answer, sources = answer_question(question,similarity_threshold)

    return {
        "question" : question,
        "answer" : answer,
        "source" : [
            { "Sources" : r.payload['source'] , "score" : round(r.score,3)}
            for r in sources

        ]
    }