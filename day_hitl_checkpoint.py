import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from day15_rag import retrieve, build_prompt, generate_with_groq

load_dotenv()

BORDERLINE_LOW = 0.3
BORDERLINE_HIGH = 0.45 # scores between this interval needs human review rather than automatic refusal or genration

class HITLState(TypedDict):
    question: str
    retrieved_chunks: str
    top_score: str
    human_approved: bool
    answer: str


def retrieve_node(state: HITLState) -> dict:
    chunks, top_score = retrieve(state["question"])
    plain_chunks = [
        {"text": c.payload["text"],"source": c.payload["source"],"score": c.score}
        for c in chunks
    ]
    return {"retrieved_chunks": plain_chunks, "top_score": top_score}

def human_review_node(state: HITLState) -> dict:
    top_chunk_text = state["retrieved_chunks"][0]["text"][:200] if state["retrieved_chunks"] else "N/A"
    decision = interrupt({
        "question": state["question"],
        "top_score": round(state["top_score"], 3),
        "top_chunk_preview": top_chunk_text,
        "message": "Score is borderline. Approve generating an answer? (True/False)"
    })
    return {"human_approved": decision}

def generate_node(state: HITLState) -> dict:
    context = "\n\n".join(f"[Source: {c['source']}\n{c['text']}]" for c in state["retrieved_chunks"])
    prompt=f"""Answer question using ONLY thecontext below.
    If you answer isn't in the context, say "I don't have information about that in my documents
    
    Context: {context}
    
    Question : {state['question']}
    """
    answer = generate_with_groq(prompt)
    return {"answer": answer}

def refuse_node(state: HITLState) -> dict:
    return {"answer": "I don't have information about that in my documents."}

def route_after_retrieve(state: HITLState) -> dict:
    score = state["top_score"]
    if score < BORDERLINE_LOW:
        return "refuse"
    elif score < BORDERLINE_HIGH:
        return "human_review"
    else:
        return "generate"

def route_after_human(state: HITLState) -> dict:
    return "generate" if state["human_approved"] else "refuse"
graph = StateGraph(HITLState)
graph.add_node("retrieve",retrieve_node)
graph.add_node("human_review",human_review_node)
graph.add_node("generate",generate_node)
graph.add_node("refuse", refuse_node)

graph.set_entry_point("retrieve")
graph.add_conditional_edges("retrieve", route_after_retrieve,{
    "refuse":"refuse",
    "human_review":"human_review",
    "generate":"generate"
})

graph.add_conditional_edges("human_review", route_after_human,{
    "generate":"generate",
    "refuse":"refuse"
})

graph.add_edge("generate",END)
graph.add_edge("refuse",END)

checkpointer = MemorySaver()
workflow = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    question = "Why does streaming feel faster even if it isn't"
    config = {"configurable": {"thread_id":"hitl-test-1"}}
    result = workflow.invoke({"question": question}, config=config)

    if "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        print("\n--- HUMAN REVIEW NEEDED ---")
        print(interrupt_info)
        raw = input("\nApprove? (y/n): ")
        approved = raw.strip().lower() == "y"
        result = workflow.invoke(Command(resume=approved), config=config)
    print(f"\nFinal answer: {result['answer']}")


#config = {"configurable": {"thread_id": "hitl-test-1"}}
#This is an ID label for "which session is this." 
#Since this workflow can pause (via interrupt()) and needs to be resumed later, 
#LangGraph needs some way to know which specific paused execution you're resuming when you call .invoke() again. 
#thread_id is just a string you pick — any unique label works. 
#Every call using the same thread_id shares the same saved, ongoing state — a different thread_id would start a completely fresh, unrelated execution.


#checkpointer = MemorySaver()
#This is what makes pausing and resuming actually possible. 
#interrupt() needs somewhere to save a snapshot of "exactly where execution was" the moment it pauses, 
#so it can restore that exact spot later when you resume. 
#MemorySaver() stores these snapshots in your Python process's own memory (RAM) — 
#free, simple, but temporary — if you closed the terminal and restarted the script, that saved snapshot would be gone 

