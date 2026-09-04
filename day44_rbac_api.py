from fastapi import FastAPI
from day42_rbac_answer import answer_with_rbac
from day43_audit_log import get_all_logs
from day44_summarize import summarize_audit_log

app = FastAPI()

@app.get("/ask")

def ask(question: str, user_role: str):
    answer, sources = answer_with_rbac(question, user_role=user_role)
    return {
        "question": question,
        "user_role": user_role,
        "answer": answer,
        "sources": [
            {"source": r.payload["source"], "score": round(r.score, 3)}
            for r in sources
        ]
    }

@app.get("/audit/logs")

def audit_logs():
    rows = get_all_logs()
    return{
        "total_entries": len(rows),
        "logs" : [
            {
            "id": r[0],
            "timestamp": r[1],
            "user_role": r[2],
            "question": r[3],
            "status": r[4],
            "sources_used": r[5]
            }

        for r in rows
        ]
    }

@app.get("/audit/summary")
def audit_summary():
    rows = get_all_logs()
    summary = summarize_audit_log(rows)
    return {"summary": summary}


#cases to test

#uvicorn day44_rbac_api:app --reload
# curl -G "localhost:8000/ask" --data-urlencode "question=How do I control who can access my S3 bucket?" --data-urlencode "user_role=engineer"

# curl -G "localhost:8000/ask" --data-urlencode "question=What did I learn about async programming?" --data-urlencode "user_role=admin"

# curl "localhost:8000/audit/summary"

# curl "localhost:8000/audit/logs"