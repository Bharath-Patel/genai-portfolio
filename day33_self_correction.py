import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict
from day15_rag import answer_question

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

class WorkflowState(TypedDict):
    topic: str
    research_findings: str
    final_post: str
    revision_count: int
    feedback: str

def research_node(state: WorkflowState) -> dict:
    print(">>> Running research_node")
    answer, sources = answer_question(state["topic"])
    return {"research_findings": answer, "revision_count": 0}

def draft_node(state: WorkflowState) -> dict:
    print(f">>> Running draft_node (attempt {state['revision_count'] + 1})")

    feedback_note = ""
    if state.get("feedback"):
        feedback_note = f"\n\nPrevious attempt was rejected for this reason: {state['feedback']}. Please fix this."

    prompt = f"""Based on this research, write a short, engaging LinkedIn post (3-4 sentences, casual professional tone).
This is not a real business scenario - it's a technical learning demo, so keep it lighthearted and clearly framed as a personal learning post.

Research: {state['research_findings']}{feedback_note}
"""
    response = llm.invoke(prompt)
    return {
        "final_post": response.content,
        "revision_count": state["revision_count"] + 1
    }

def check_node(state: WorkflowState) -> dict:
    print(">>> Running check_node")

    if "don't have information" in state["research_findings"]:
        return {"feedback": "PASS"}  # nothing to check if research failed - accept as-is

    check_prompt = f"""Does this LinkedIn post specifically reference real details from the research below, 
rather than being generic/vague? Answer with exactly "PASS" or explain what's missing in one sentence.

Research: {state['research_findings']}
Post: {state['final_post']}
"""
    response = llm.invoke(check_prompt)
    return {"feedback": response.content.strip()}

def route_after_check(state: WorkflowState) -> str:
    if state["feedback"] == "PASS" or state["revision_count"] >= 3:
        return "end"
    return "retry"

# Wire the graph
graph = StateGraph(WorkflowState)
graph.add_node("research", research_node)
graph.add_node("draft", draft_node)
graph.add_node("check", check_node)

graph.set_entry_point("research")
graph.add_edge("research", "draft")
graph.add_edge("draft", "check")

# THIS is new - a conditional edge, branching based on route_after_check's return value
graph.add_conditional_edges(
    "check",
    route_after_check,
    {"end": END, "retry": "draft"}
)

workflow = graph.compile()

if __name__ == "__main__":
    result = workflow.invoke({"topic": "How do I control who can access my S3 bucket?"})
    print(f"\n=== Final Post (after {result['revision_count']} attempt(s)) ===")
    print(result["final_post"])
    print(f"\nFinal check feedback: {result['feedback']}")